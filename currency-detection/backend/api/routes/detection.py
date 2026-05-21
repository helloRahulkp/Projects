"""
Detection API routes — image, batch, webcam frame, annotation.
"""
import io
import base64
import numpy as np
import cv2
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional

from backend.detection.detect_image import ImageDetector
from backend.services.analytics_service import analytics_service
from backend.core.config import settings
from backend.core.logger import logger

router = APIRouter()

# Lazy-load detector
_detector: Optional[ImageDetector] = None

def get_detector() -> ImageDetector:
    global _detector
    if _detector is None:
        _detector = ImageDetector()
    return _detector


async def _read_image(upload: UploadFile) -> np.ndarray:
    """Read an UploadFile and decode to BGR numpy array."""
    if not upload.content_type.startswith("image/"):
        raise HTTPException(400, detail=f"'{upload.filename}' is not an image file.")
    contents = await upload.read()
    arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, detail=f"Cannot decode image: {upload.filename}")
    return img


@router.post("/image", summary="Detect currency in a single image")
async def detect_image(
    file: UploadFile = File(...),
    confidence: float = Query(None, ge=0.0, le=1.0),
    annotated: bool = Query(False, description="Return annotated image as base64"),
):
    detector = get_detector()
    img = await _read_image(file)
    results = detector.process_image(img, conf_threshold=confidence, return_annotated=annotated)

    annotated_b64 = None
    if annotated and results.get("annotated_image") is not None:
        ann_img = results.pop("annotated_image")
        _, buf = cv2.imencode(".jpg", ann_img)
        annotated_b64 = base64.b64encode(buf.tobytes()).decode()
    else:
        results.pop("annotated_image", None)

    analytics_service.record(results, source="image_upload")

    return {
        "success": True,
        "filename": file.filename,
        "data": results,
        "annotated_image_b64": annotated_b64,
    }


@router.post("/batch", summary="Detect currency in multiple images")
async def detect_batch(
    files: List[UploadFile] = File(...),
    confidence: float = Query(None, ge=0.0, le=1.0),
):
    if len(files) > 20:
        raise HTTPException(400, detail="Maximum 20 images per batch.")

    detector = get_detector()
    results_list = []
    grand_total_amount = 0
    grand_total_count = 0
    combined_summary: dict = {}

    for f in files:
        try:
            img = await _read_image(f)
            res = detector.process_image(img, conf_threshold=confidence)
            res.pop("annotated_image", None)
            results_list.append({"filename": f.filename, "data": res})
            grand_total_amount += res["total_amount"]
            grand_total_count += res["total_count"]
            for k, v in res["summary"].items():
                combined_summary[k] = combined_summary.get(k, 0) + v
        except HTTPException as e:
            results_list.append({"filename": f.filename, "error": e.detail})
        except Exception as e:
            logger.error(f"Batch item error ({f.filename}): {e}")
            results_list.append({"filename": f.filename, "error": str(e)})

    batch_result = {
        "total_amount": grand_total_amount,
        "total_count": grand_total_count,
        "summary": combined_summary,
        "currency": "INR",
    }
    analytics_service.record(batch_result, source="batch_upload")

    return {
        "success": True,
        "total_images": len(files),
        "grand_total_amount": grand_total_amount,
        "grand_total_count": grand_total_count,
        "combined_summary": combined_summary,
        "results": results_list,
    }


@router.post("/frame", summary="Detect currency in a webcam frame (base64)")
async def detect_frame(payload: dict):
    """
    Accepts a base64-encoded JPEG frame from the webcam and returns detections.
    Expected payload: {"frame_b64": "...", "confidence": 0.45}
    """
    frame_b64 = payload.get("frame_b64")
    confidence = payload.get("confidence", settings.CONFIDENCE_THRESHOLD)

    if not frame_b64:
        raise HTTPException(400, detail="frame_b64 is required.")

    try:
        img_bytes = base64.b64decode(frame_b64)
        arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Cannot decode frame")
    except Exception as e:
        raise HTTPException(400, detail=f"Invalid frame: {e}")

    detector = get_detector()
    results = detector.process_image(img, conf_threshold=confidence, return_annotated=True)

    annotated_b64 = None
    ann_img = results.pop("annotated_image", None)
    if ann_img is not None:
        _, buf = cv2.imencode(".jpg", ann_img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        annotated_b64 = base64.b64encode(buf.tobytes()).decode()

    return {
        "success": True,
        "data": results,
        "annotated_frame_b64": annotated_b64,
    }


@router.get("/info", summary="Model metadata")
async def model_info():
    return {
        "model_path": settings.MODEL_PATH,
        "classes": settings.CLASS_NAMES,
        "num_classes": len(settings.CLASS_NAMES),
        "device": settings.DEVICE,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
    }
