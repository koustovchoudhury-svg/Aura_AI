import os
import httpx

HOST_AGENT_URL   = os.getenv("HOST_AGENT_URL", "http://host.docker.internal:5678")
HOST_AGENT_TOKEN = os.getenv("HOST_AGENT_TOKEN", "aura-host-secret-change-me")


async def call_host_agent(endpoint: str, payload: dict) -> dict:
    """Call the AURA Host Companion Agent running on the Windows host."""
    headers = {"Authorization": f"Bearer {HOST_AGENT_TOKEN}"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(f"{HOST_AGENT_URL}/{endpoint}", json=payload, headers=headers)
            resp.raise_for_status()
            return {"success": True, **resp.json()}
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"{e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Host agent unreachable: {e}. Is host_agent/main.py running on Windows?"}
