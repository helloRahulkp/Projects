from pathlib import Path
from ultralytics import YOLO
from src.core.config import settings
from src.core.logger import logger

def export_model():
    """
    Exports the trained YOLOv8 PyTorch model to production-ready formats.
    Optimized for ONNX and TorchScript.
    """
    logger.info("Starting Model Export Process...")

    # 1. Define Paths
    model_path = Path(settings.YOLO_MODEL_PATH)
    
    if not model_path.exists():
        logger.error(f"Export failed: Source model not found at {model_path}")
        return

    try:
        # 2. Load the Best Trained Model
        logger.info(f"Loading model from {model_path} for export...")
        model = YOLO(model_path)

        # 3. Export to ONNX
        # ONNX is the standard for cross-platform inference and FastAPI deployment
        logger.info("Exporting to ONNX format...")
        onnx_path = model.export(
            format="onnx",
            imgsz=640,
            dynamic=True,  # Allows for variable batch sizes/resolutions
            opset=12
        )
        logger.info(f"ONNX export completed: {onnx_path}")

        # 4. Export to TorchScript
        # TorchScript is ideal for high-performance C++ or Python production environments
        logger.info("Exporting to TorchScript format...")
        ts_path = model.export(
            format="torchscript",
            imgsz=640
        )
        logger.info(f"TorchScript export completed: {ts_path}")

        # 5. CoreML Export (Optional - Specific for Apple Silicon/M1 Pro)
        # Allows for maximum hardware acceleration on macOS/iOS devices
        if "mps" in settings.DEVICE.lower() or Path("/usr/bin/sw_vers").exists():
            logger.info("Apple Silicon detected. Exporting to CoreML...")
            coreml_path = model.export(format="coreml")
            logger.info(f"CoreML export completed: {coreml_path}")

    except Exception as e:
        logger.exception(f"An error occurred during model export: {e}")

if __name__ == "__main__":
    export_model()