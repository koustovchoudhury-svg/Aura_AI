import os
from fastapi import APIRouter, UploadFile, File, Depends, Response, HTTPException
from packages.voice.stt import transcribe_audio
from packages.voice.tts import synthesize_speech
from pydantic import BaseModel
from .auth import get_current_user

router = APIRouter()

class SpeakRequest(BaseModel):
    text: str
    voice_id: str = "en_US-lessac-medium"

@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    user=Depends(get_current_user)
):
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")
    ext = os.path.splitext(audio.filename or "")[1] or ".webm"
    try:
        result = await transcribe_audio(audio_bytes, suffix=ext)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {e}")
    return result

@router.post("/speak")
async def speak(
    req: SpeakRequest,
    user=Depends(get_current_user)
):
    audio_bytes = await synthesize_speech(req.text, req.voice_id)
    return Response(content=audio_bytes, media_type="audio/wav")
