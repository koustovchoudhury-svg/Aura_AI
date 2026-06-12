import asyncio, os, tempfile

async def synthesize_speech(text: str, voice_id: str = "en_US-lessac-medium") -> bytes:
    piper     = os.getenv("PIPER_PATH","piper")
    models    = os.getenv("PIPER_MODELS_DIR","/tmp/piper_models")
    model_path = f"{models}/{voice_id}.onnx"
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out = f.name
    try:
        proc = await asyncio.create_subprocess_exec(
            piper,"--model",model_path,"--output_file",out,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate(input=text.encode())
        if os.path.exists(out):
            return open(out,"rb").read()
        return b""
    finally:
        if os.path.exists(out): os.unlink(out)
