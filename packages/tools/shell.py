import asyncio

MAX_OUTPUT = 4000

async def run_shell(command: str, timeout: int = 30) -> dict:
    """Execute a shell command inside the API container (sandboxed)."""
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            return {"success": False, "stdout": "", "stderr": f"Command timed out after {timeout}s", "exit_code": -1}

        out = stdout.decode(errors="replace")[:MAX_OUTPUT]
        err = stderr.decode(errors="replace")[:MAX_OUTPUT]
        return {"success": proc.returncode == 0, "stdout": out, "stderr": err, "exit_code": proc.returncode}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}
