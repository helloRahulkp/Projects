from pathlib import Path
from ultralytics import YOLO
from src.core.config import settings
from src.core.logger import logger

def evaluate_model():
    """
    Evaluates the trained YOLOv8 model on the test dataset.
    Generates mAP, Precision, Recall metrics and confusion matrices.
    """
    logger.info("Starting Model Evaluation Phase...")

    # 1. Define Paths
    model_path = Path(settings.YOLO_MODEL_PATH)
    dataset_yaml = Path(settings.BASE_DIR) / "dataset" / "dataset.yaml"

    if not model_path.exists():
        logger.error(f"Evaluation failed: Model weights not found at {model_path}")
        return

    # 2. Load the trained model
    try:
        logger.info(f"Loading model from {model_path} for validation...")
        model = YOLO(model_path)

        # 3. Run Validation on the test set
        # We set split='test' to use the held-out data defined in dataset.yaml
        metrics = model.val(
            data=str(dataset_yaml),
            split='test',
            imgsz=640,
            batch=16,
            device=settings.DEVICE,
            project="outputs/evaluation",
            name="test_results",
            exist_ok=True,
            save_json=True  # Saves detailed results for further analysis
        )

        # 4. Log Key Metrics
        logger.info("--- Evaluation Metrics ---")
        logger.info(f"mAP50-95: {metrics.box.map:.4f}")
        logger.info(f"mAP50:    {metrics.box.map50:.4f}")
        logger.info(f"Precision: {metrics.box.mp:.4f}")
        logger.info(f"Recall:    {metrics.box.mr:.4f}")
        
        logger.info(f"Evaluation artifacts saved to: outputs/evaluation/test_results")

    except Exception as e:
        logger.exception(f"An error occurred during evaluation: {e}")

if __name__ == "__main__":
    evaluate_model()