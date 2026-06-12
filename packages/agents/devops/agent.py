from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import AgentManifest, ToolManifest, PermissionLevel, CostTier
from packages.tools.llm import get_llm
from packages.tools.kubectl import kubectl_get
from packages.tools.shell import run_shell
from packages.tools.host_agent import call_host_agent

class DevOpsAgent(BaseAgent):
    manifest = AgentManifest(
        name="DevOpsAgent",
        description="Kubernetes, Terraform, AWS/Azure, CI/CD, incident management",
        intents=["devops","kubernetes","infrastructure","incident","deployment","monitoring","cicd"],
        keywords=["kubectl","pod","deploy","cluster","terraform","aws","azure","ci","cd","jenkins","pipeline","restart","scale","logs","metrics","helm","namespace"],
        tools=[
            ToolManifest(name="kubectl_get",description="Read Kubernetes resources",
                         permission=PermissionLevel.READ_ONLY,cost_tier=CostTier.FREE),
            ToolManifest(name="kubectl_delete",description="Delete Kubernetes resource",
                         permission=PermissionLevel.APPROVAL_REQUIRED,cost_tier=CostTier.FREE),
            ToolManifest(name="terraform_plan",description="Run terraform plan",
                         permission=PermissionLevel.READ_ONLY,cost_tier=CostTier.FREE),
            ToolManifest(name="terraform_apply",description="Apply terraform",
                         permission=PermissionLevel.APPROVAL_REQUIRED,cost_tier=CostTier.FREE),
            ToolManifest(name="execute_shell",description="Run a shell command in the AURA sandbox",
                         permission=PermissionLevel.APPROVAL_REQUIRED,cost_tier=CostTier.FREE,
                         timeout_seconds=30),
            ToolManifest(name="host_action",description="Open apps/URLs or read/write/list files on the user's host machine via the companion agent",
                         permission=PermissionLevel.APPROVAL_REQUIRED,cost_tier=CostTier.FREE,
                         timeout_seconds=20),
        ],
        preferred_model="auto", max_permission=PermissionLevel.APPROVAL_REQUIRED,
        tags=["devops","infrastructure"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm         = get_llm()
        system      = self._build_system_prompt(context)
        tool_calls  = []

        if "host_action" in task.tools:
            action = task.metadata.get("action", "")
            endpoint_map = {
                "open_app":  ("open_app",  {"name": task.metadata.get("target", "")}),
                "open_url":  ("open_url",  {"url": task.metadata.get("target", "")}),
                "list_dir":  ("list_dir",  {"path": task.metadata.get("target", "")}),
                "read_file": ("read_file", {"path": task.metadata.get("target", "")}),
                "write_file": ("write_file", {"path": task.metadata.get("target", ""),
                                               "content": task.metadata.get("content", "")}),
            }
            if action not in endpoint_map:
                return AgentResult(success=False, output=None,
                                   error=f"Unknown host_action '{action}'. Valid: {list(endpoint_map)}")
            endpoint, payload = endpoint_map[action]
            result = await call_host_agent(endpoint, payload)
            tool_calls.append({"tool": "host_action", "action": action,
                               "status": "ok" if result.get("success") else "error"})
            if not result.get("success"):
                return AgentResult(success=False, output=None, tool_calls=tool_calls,
                                   error=result.get("error", "Host action failed"))
            return AgentResult(success=True, output=result, tool_calls=tool_calls)

        if "execute_shell" in task.tools:
            command = task.metadata.get("command", task.description)
            result  = await run_shell(command)
            tool_calls.append({"tool":"execute_shell","status":"ok" if result["success"] else "error","command":command})
            output = f"$ {command}\n\n{result['stdout']}"
            if result["stderr"]:
                output += f"\n--- stderr ---\n{result['stderr']}"
            return AgentResult(success=result["success"], output=output, tool_calls=tool_calls,
                               metadata={"exit_code": result["exit_code"]})

        cluster_ctx = ""
        try:
            pods = await kubectl_get("pods","--all-namespaces")
            cluster_ctx = f"Cluster state:\n{pods}"
            tool_calls.append({"tool":"kubectl_get","status":"ok"})
        except Exception:
            cluster_ctx = "Cluster info unavailable"
            tool_calls.append({"tool":"kubectl_get","status":"skipped"})
        try:
            prompt = f"{cluster_ctx}\n\nTask: {task.description}\n\nProvide: root cause analysis, recommended actions, exact commands, prevention."
            response = await llm.ainvoke([SystemMessage(content=system+"\nYou are an expert DevOps/SRE engineer."),
                                          HumanMessage(content=prompt)])
            tool_calls.append({"tool":"llm_analysis","status":"ok"})
            return AgentResult(success=True, output=response.content, tool_calls=tool_calls)
        except Exception as e:
            return AgentResult(success=False, output=None, tool_calls=tool_calls, error=str(e))
