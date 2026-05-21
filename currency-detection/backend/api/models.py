"""
Pydantic models for API validation and serialization.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---- Detection ----

class DetectionBox(BaseModel):
    label: str
    display: str
    confidence: float
    box: List[float]
    color: List[int]
    denomination: int


class DetectionResult(BaseModel):
    detections: List[DetectionBox]
    summary: Dict[str, int]
    total_count: int
    total_amount: int
    currency: str = "INR"


class ImageDetectionResponse(BaseModel):
    success: bool
    filename: str
    data: DetectionResult


class BatchDetectionItem(BaseModel):
    filename: str
    data: DetectionResult


class BatchDetectionResponse(BaseModel):
    success: bool
    total_images: int
    grand_total_amount: int
    grand_total_count: int
    combined_summary: Dict[str, int]
    results: List[BatchDetectionItem]


# ---- Currency Conversion ----

class ConversionRequest(BaseModel):
    amount: float = Field(..., gt=0)
    from_currency: str = "INR"
    to_currency: str = "USD"


class ConversionResult(BaseModel):
    from_currency: str
    to_currency: str
    original_amount: float
    converted_amount: float
    rate: float
    source: str


class MultiConversionResponse(BaseModel):
    base_amount: float
    base_currency: str
    conversions: Dict[str, ConversionResult]


# ---- TTS ----

class TTSRequest(BaseModel):
    text: str
    detections: Optional[List[Dict[str, Any]]] = None
    total_amount: Optional[int] = None


class TTSResponse(BaseModel):
    success: bool
    audio_b64: Optional[str]
    format: Optional[str]
    text: str


# ---- Analytics ----

class AnalyticsStats(BaseModel):
    total_sessions: int
    total_amount_detected: float
    avg_amount_per_session: float
    denomination_counts: Dict[str, int]
    recent_trend: List[Dict[str, Any]]


# ---- Health ----

class HealthResponse(BaseModel):
    status: str
    version: str
    device: str
    model_loaded: bool
