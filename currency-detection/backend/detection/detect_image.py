"""
Image detection engine using YOLOv8.
Supports single and batch image processing.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional

from ultralytics import YOLO

from backend.core.config import settings
from backend.core.constants import DENOMINATION_VALUES, CURRENCY_COLORS, DENOMINATION_DISPLAY
from backend.core.logger import logger


class ImageDetector:
    """
    YOLOv8-based currency detection engine.
    Singleton pattern — load model once, reuse across requests.
    """
    _instance: Optional["ImageDetector"] = None

    def __new__(cls, model_path: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path: str = None):
        if self._initialized:
            return
        self.model_path = model_path or settings.MODEL_PATH
        self.device = settings.DEVICE
        self._load_model()
        self._initialized = True

    def _load_model(self):
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"YOLO model loaded from '{self.model_path}' on device='{self.device}'")
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            raise RuntimeError(f"Cannot initialize detector: {e}")

    def process_image(
        self,
        image: np.ndarray,
        conf_threshold: float = None,
        return_annotated: bool = False,
    ) -> Dict[str, Any]:
        """
        Run detection on a BGR numpy image.

        Returns a structured dict with detections, summary, totals.
        """
        threshold = conf_threshold if conf_threshold is not None else settings.CONFIDENCE_THRESHOLD

        results = self.model.predict(
            source=image,
            conf=threshold,
            iou=settings.IOU_THRESHOLD,
            device=self.device,
            verbose=False,
        )

        detections = []
        summary: Dict[str, int] = {}
        total_amount = 0

        result = results[0]
        for box in result.boxes:
            cls_id = int(box.cls[0])
            if cls_id >= len(settings.CLASS_NAMES):
                continue
            label = settings.CLASS_NAMES[cls_id]
            confidence = float(box.conf[0])
            coords = [round(c, 1) for c in box.xyxy[0].tolist()]
            color = list(CURRENCY_COLORS.get(label, (255, 255, 255)))
            denomination = DENOMINATION_VALUES.get(label, 0)

            summary[label] = summary.get(label, 0) + 1
            total_amount += denomination

            detections.append({
                "label": label,
                "display": DENOMINATION_DISPLAY.get(label, label),
                "confidence": round(confidence, 2),
                "box": coords,
                "color": color,
                "denomination": denomination,
            })

        annotated = None
        if return_annotated:
            annotated = self._draw_detections(image, detections)

        return {
            "detections": detections,
            "summary": summary,
            "total_count": len(detections),
            "total_amount": total_amount,
            "currency": "INR",
            "annotated_image": annotated,
        }

    def process_batch(
        self,
        images: List[np.ndarray],
        conf_threshold: float = None,
    ) -> List[Dict[str, Any]]:
        """Process multiple images and return per-image results."""
        return [self.process_image(img, conf_threshold) for img in images]

    def _draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Draw bounding boxes with labels on image (BGR)."""
        annotated = image.copy()
        for det in detections:
            x1, y1, x2, y2 = map(int, det["box"])
            label = det["label"]
            conf = det["confidence"]
            color = tuple(det["color"])

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
            text = f"{label} {conf:.0%}"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
            cv2.rectangle(annotated, (x1, y1 - th - 10), (x1 + tw + 4, y1), color, -1)
            cv2.putText(annotated, text, (x1 + 2, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        return annotated
