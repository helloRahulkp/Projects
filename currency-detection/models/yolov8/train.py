import os
import torch
import numpy as np
from ultralytics import YOLO
from src.core.config import settings
from src.core.logger import logger

# --- THE ULTIMATE PYTORCH 2.6+ MONKEY PATCH ---
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

# --- NUMPY 2.0 DEPRECATION MONKEY PATCH ---
if not hasattr(np, 'trapz') and hasattr(np, 'trapezoid'):
    np.trapz = np.trapezoid
    logger.info("Successfully patched NumPy 2.0+ trapz deprecation.")

def train_yolo():
    logger.info("Initializing YOLOv8 Training Pipeline...")

    if torch.backends.mps.is_available():
        device_target = "mps"
    else:
        device_target = "cpu"
        
    logger.info(f"Using forced hardware target: {device_target.upper()}")

    model_variant = "yolov8s.pt"
    logger.info(f"Loading base weights configuration: {model_variant}")
    
    model = YOLO(model_variant)

    # Begin Training with clean local overrides 
    model.train(
        data="dataset/dataset.yaml",
        epochs=50,         # Directly setting 50 epochs for stable convergence
        imgsz=640,         # Standard YOLOv8 image size resolution
        batch=16,          # Optimized for M1 Pro memory bandwidth
        device=device_target,
        workers=2,
        plots=True
    )
    
    logger.info("Model training loop finished execution.")

if __name__ == "__main__":
    train_yolo()
