import torch
import numpy as np
from ultralytics import YOLO
import sys

# --- THE PYTORCH 2.6+ PATCH ---
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

# --- NUMPY 2.0 PATCH ---
if not hasattr(np, 'trapz') and hasattr(np, 'trapezoid'):
    np.trapz = np.trapezoid

def run_prediction():
    try:
        # Load your BEST trained weights
        model = YOLO("runs/detect/train2/weights/best.pt")

        # Run inference
        results = model.predict(
            source='/Users/rahulkpkurup/Downloads/download.jpeg',
            conf=0.25,
            save=True
        )
        
        print(f"\n🚀 Success! Prediction saved to: {results[0].save_dir}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    run_prediction()
