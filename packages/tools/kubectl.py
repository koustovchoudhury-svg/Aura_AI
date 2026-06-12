import asyncio, shutil

async def kubectl_get(resource: str, namespace: str = "default") -> str:
    if not shutil.which("kubectl"):
        return "kubectl not available in this environment"
    proc = await asyncio.create_subprocess_exec(
        "kubectl","get",resource,"-n",namespace,"-o","wide",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    return out.decode() if proc.returncode == 0 else err.decode()

async def kubectl_describe(resource: str, name: str, namespace: str = "default") -> str:
    if not shutil.which("kubectl"):
        return "kubectl not available"
    proc = await asyncio.create_subprocess_exec(
        "kubectl","describe",resource,name,"-n",namespace,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    return out.decode() if proc.returncode == 0 else err.decode()
