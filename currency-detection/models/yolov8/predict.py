import cv2
from pathlib import Path
from ultralytics import YOLO
from src.core.config import settings
from src.core.logger import logger

class CurrencyPredictor:
    """
    Handles inference logic for Indian Currency detection using YOLOv8.
    """

    def __init__(self, model_path: str = None):
        # Fallback to settings if no path provided
        self.model_path = model_path or settings.YOLO_MODEL_PATH
        
        if not Path(self.model_path).exists():
            logger.error(f"Model weight not found at {self.model_path}")
            raise FileNotFoundError(f"Missing weights: {self.model_path}")
            
        logger.info(f"Loading YOLOv8 model from {self.model_path}")
        self.model = YOLO(self.model_path)
        
        # Determine device (MPS for M1 Pro, else CPU/CUDA)
        self.device = settings.DEVICE
        logger.info(f"Predictor initialized on device: {self.device}")

    def predict(self, source: str, save: bool = True, conf: float = None):
        """
        Runs detection on a single image or directory.
        
        Args:
            source: Path to image or folder.
            save: Whether to save the visualized result.
            conf: Confidence threshold override.
        """
        threshold = conf or settings.CONFIDENCE_THRESHOLD
        
        logger.info(f"Running inference on: {source}")
        results = self.model.predict(
            source=source,
            conf=threshold,
            iou=settings.IOU_THRESHOLD,
            device=self.device,
            save=save,
            project="outputs",
            name="predictions",
            exist_ok=True
        )
        
        for result in results:
            detections_count = len(result.boxes)
            logger.info(f"Detected {detections_count} notes in {result.path}")
            
            # Log individual denominations found
            if detections_count > 0:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    label = settings.CLASS_NAMES[cls_id]
                    confidence = float(box.conf[0])
                    logger.debug(f"Found {label} with {confidence:.2f} confidence")

        return results

if __name__ == "__main__":
    # Test prediction logic
    try:
        predictor = CurrencyPredictor()
        
        # Example: Predict on the first image in the test set
        test_img_dir = Path(settings.PROCESSED_DATA_DIR) / "test" / "images"
        if test_img_dir.exists():
            images = list(test_img_dir.glob("*.jpg"))
            if images:
                predictor.predict(source=str(images[0]))
            else:
                logger.warning("No images found in test directory to predict.")
        else:
            logger.warning("Test directory not found. Please run preprocessing first.")
            
    except Exception as e:
        logger.exception(f"Prediction script failed: {e}")