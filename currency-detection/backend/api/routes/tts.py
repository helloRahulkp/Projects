"""
Text-to-speech API routes.
"""
from fastapi import APIRouter
from backend.services.tts_service import tts_base64, build_detection_speech

router = APIRouter()


@router.post("/speak", summary="Generate TTS audio for detections")
async def speak(payload: dict):
    """
    Payload: {
      "text": "optional custom text",
      "detections": [...],
      "total_amount": 500
    }
    Returns base64-encoded audio.
    """
    text = payload.get("text")
    detections = payload.get("detections", [])
    total_amount = payload.get("total_amount", 0)

    if not text:
        text = build_detection_speech(detections, total_amount)

    result = await tts_base64(text)
    return result


@router.post("/speak-text", summary="Convert arbitrary text to speech")
async def speak_text(payload: dict):
    text = payload.get("text", "Hello from AI Currency Detector.")
    result = await tts_base64(text)
    return result
