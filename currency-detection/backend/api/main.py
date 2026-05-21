"""
FastAPI Application — AI Currency Detection & Voice Assistant System v2.0
"""
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.logger import logger
from backend.api.routes import detection, conversion, tts, analytics, health


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=(
            "AI-powered multi-currency detection, counting, live conversion, "
            "and voice announcement system."
        ),
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request timing middleware ─────────────────────────────────────────────
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        t0 = time.time()
        response = await call_next(request)
        ms = (time.time() - t0) * 1000
        logger.info(f"{request.method} {request.url.path} → {response.status_code} ({ms:.1f}ms)")
        return response

    # ── Global exception handler ──────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exc_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(exc)},
        )

    # ── Routes ────────────────────────────────────────────────────────────────
    app.include_router(health.router,     prefix="/api/v1",            tags=["System"])
    app.include_router(detection.router,  prefix="/api/v1/detection",  tags=["Detection"])
    app.include_router(conversion.router, prefix="/api/v1/conversion", tags=["Conversion"])
    app.include_router(tts.router,        prefix="/api/v1/tts",        tags=["TTS"])
    app.include_router(analytics.router,  prefix="/api/v1/analytics",  tags=["Analytics"])

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "device": settings.DEVICE,
            "docs": "/docs",
        }

    # ── Startup ───────────────────────────────────────────────────────────────
    @app.on_event("startup")
    async def startup():
        logger.info(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} starting on device={settings.DEVICE}")
        # Pre-warm the detector
        try:
            from backend.detection.detect_image import ImageDetector
            ImageDetector()
            logger.info("✅ Model pre-loaded successfully.")
        except Exception as e:
            logger.warning(f"⚠️  Model pre-load failed (will retry on first request): {e}")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=1,
    )
