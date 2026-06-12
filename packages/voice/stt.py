import asyncio, os, tempfile

_model = None

def get_whisper():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("base", device="cpu", compute_type="int8",
                              download_root="/tmp/whisper_models")
    return _model

async def transcribe_audio(audio_bytes: bytes, language: str = "en", suffix: str = ".webm") -> dict:
    model = get_whisper()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes); tmp = f.name
    try:
        segs, info = model.transcribe(tmp, language=language, beam_size=5, vad_filter=True)
        return {"transcript": " ".join(s.text for s in segs).strip(),
                "language": info.language, "duration": info.duration}
    finally:
        os.unlink(tmp)

async def transcribe_file(file_path: str, language: str = "en") -> dict:
    model = get_whisper()
    segs, info = model.transcribe(file_path, language=language, beam_size=5, vad_filter=True)
    seg_list = [{"start":s.start,"end":s.end,"text":s.text.strip()} for s in segs]
    return {"transcript": " ".join(s["text"] for s in seg_list),
            "segments": seg_list, "language": info.language, "duration": info.duration}
