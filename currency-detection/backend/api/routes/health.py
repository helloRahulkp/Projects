"""
Health check routes.
"""
import platform
import psutil
from fastapi import APIRouter
from backend.core.config import settings

router = APIRouter()


@router.get("/health", summary="System health check")
async def health():
    model_loaded = False
    try:
        from backend.detection.detect_image import ImageDetector
        d = ImageDetector()
        model_loaded = d._initialized
    except Exception:
        pass

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "device": settings.DEVICE,
        "model_loaded": model_loaded,
        "platform": platform.system(),
        "python": platform.python_version(),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "ram_percent": psutil.virtual_memory().percent,
    }


@router.get("/ping", summary="Simple ping")
async def ping():
    return {"pong": True}
