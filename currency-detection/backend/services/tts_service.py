"""
Text-to-speech service.
Uses gTTS (online) with pyttsx3 as offline fallback.
Returns audio bytes that can be served to browser via base64.
"""
import io
import base64
import platform
from typing import Optional, Tuple

from backend.core.logger import logger
from backend.core.constants import NUMBER_WORDS, DENOMINATION_VALUES


def _number_to_words(n: int) -> str:
    """Convert a number to spoken English words."""
    if n in NUMBER_WORDS:
        return NUMBER_WORDS[n]
    # Generic fallback
    return str(n)


def build_detection_speech(detections: list, total_amount: int) -> str:
    """Build a natural TTS message from detection results."""
    if not detections:
        return "No currency notes detected."

    parts = []
    # Group by denomination
    counts: dict = {}
    for det in detections:
        denom = det.get("denomination", 0)
        counts[denom] = counts.get(denom, 0) + 1

    for denom, count in sorted(counts.items()):
        word = _number_to_words(denom)
        note_str = "note" if count == 1 else "notes"
        parts.append(f"{count} {word} rupee {note_str}")

    joined = ", ".join(parts)
    total_words = _number_to_words(total_amount) if total_amount in NUMBER_WORDS else str(total_amount)
    return f"Detected {joined}. Total amount is {total_words} rupees."


def build_total_speech(total_amount: int, currency: str = "INR") -> str:
    total_words = _number_to_words(total_amount) if total_amount in NUMBER_WORDS else str(total_amount)
    return f"Total amount is {total_words} rupees."


async def text_to_speech_bytes(text: str) -> Tuple[Optional[bytes], str]:
    """
    Convert text to speech audio bytes.
    Returns (audio_bytes, format) or (None, '') on failure.

    Strategy:
      1. Try gTTS (online) → mp3
      2. Fall back to pyttsx3 (offline) → wav via temp file
    """
    # --- Strategy 1: gTTS (works on all platforms, needs internet) ---
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        tts = gTTS(text=text, lang="en", slow=False)
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read(), "mp3"
    except Exception as e:
        logger.debug(f"gTTS failed: {e}. Trying pyttsx3...")

    # --- Strategy 2: pyttsx3 (offline, cross-platform) ---
    try:
        import pyttsx3
        import tempfile
        import os

        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        engine.stop()

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp_path)
        return audio_bytes, "wav"
    except Exception as e:
        logger.warning(f"pyttsx3 also failed: {e}")

    return None, ""


async def tts_base64(text: str) -> dict:
    """Return TTS audio as base64 string for frontend playback."""
    audio_bytes, fmt = await text_to_speech_bytes(text)
    if audio_bytes:
        encoded = base64.b64encode(audio_bytes).decode("utf-8")
        return {"success": True, "audio_b64": encoded, "format": fmt, "text": text}
    return {"success": False, "audio_b64": None, "format": None, "text": text}
