import torch
import numpy as np
from ultralytics import YOLO
import cv2

# --- THE PYTORCH 2.6+ PATCH ---
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

# --- NUMPY 2.0 PATCH ---
if not hasattr(np, 'trapz') and hasattr(np, 'trapezoid'):
    np.trapz = np.trapezoid

def run_live():
    # Load your best weights
    model = YOLO("runs/detect/train2/weights/best.pt")

    # source=0 is usually the built-in MacBook camera
    # show=True opens the window automatically
    # conf=0.5 helps filter out "ghost" detections
    results = model.predict(source="0", show=True, stream=True, conf=0.5)

    print("Live detection started. Press 'q' on the window to stop.")

    for r in results:
        # The window will update automatically because show=True
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_live()
