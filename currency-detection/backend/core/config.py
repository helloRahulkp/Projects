"""
Core configuration for AI Currency Detection System.
Supports cross-platform (Windows, macOS, Linux) and CPU/GPU inference.
"""
import os
import platform
from pathlib import Path
from typing import List, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def detect_device() -> str:
    """Auto-detect best available compute device."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        # MPS only available natively on macOS, not in Docker
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            if platform.system() == "Darwin":
                return "mps"
    except ImportError:
        pass
    return "cpu"


class Settings(BaseSettings):
    """
    Application settings. Loads from environment variables / .env file.
    All paths use pathlib for cross-platform compatibility.
    """
    # Project Info
    PROJECT_NAME: str = "AI Currency Detection & Voice Assistant"
    VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Hardware
    DEVICE: str = Field(default_factory=detect_device)

    # Paths — use str so Docker env vars work cleanly
    BASE_DIR: Path = Path("/app")
    MODEL_PATH: str = "models/checkpoints/best.pt"

    # Detection thresholds
    CONFIDENCE_THRESHOLD: float = 0.45
    IOU_THRESHOLD: float = 0.50

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Currency conversion
    EXCHANGE_RATE_API_URL: str = "https://open.er-api.com/v6/latest"
    CURRENCY_API_KEY: Union[str, None] = None
    CONVERSION_CACHE_TTL: int = 3600  # seconds

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "outputs/logs/app.log"

    # Class names matching training labels
    CLASS_NAMES: List[str] = [
        "10_Old", "10_New", "20_Old", "20_New",
        "50_Old", "50_New", "100_Old", "100_New",
        "200", "500", "2000"
    ]

    DENOMINATION_MAP: dict = {
        "10_Old": 10, "10_New": 10,
        "20_Old": 20, "20_New": 20,
        "50_Old": 50, "50_New": 50,
        "100_Old": 100, "100_New": 100,
        "200": 200, "500": 500, "2000": 2000
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

# Ensure output directories exist
os.makedirs("outputs/logs", exist_ok=True)
os.makedirs("outputs/reports", exist_ok=True)
