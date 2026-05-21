import cv2
import numpy as np
import albumentations as A
from typing import Tuple, List, Dict
from src.core.config import settings
from src.core.logger import logger

class CurrencyAugmenter:
    """
    Provides image augmentation specifically tuned for banknote detection.
    Focuses on lighting variations, rotation, and slight distortions.
    """

    def __init__(self, img_size: int = 640):
        self.img_size = img_size
        
        # Training augmentation pipeline
        self.train_transform = A.Compose([
            # Geometric transformations
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.2),
            A.RandomRotate90(p=0.5),
            A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.2, rotate_limit=45, p=0.5),
            
            # Color/Light transformations (Critical for currency)
            A.RandomBrightnessContrast(p=0.3),
            A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.3),
            A.RGBShift(r_shift_limit=15, g_shift_limit=15, b_shift_limit=15, p=0.3),
            A.CLAHE(p=0.2),
            
            # Quality/Noise transformations
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.2),
            A.Blur(blur_limit=3, p=0.2),
            A.ImageCompression(quality_lower=60, p=0.2),
            
            # Resize to model input size
            A.Resize(height=self.img_size, width=self.img_size),
        ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

        # Validation/Inference pipeline (Standardization only)
        self.val_transform = A.Compose([
            A.Resize(height=self.img_size, width=self.img_size),
        ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

    def augment_image(self, image: np.ndarray, bboxes: List[List[float]], class_labels: List[int]) -> Tuple[np.ndarray, List[List[float]]]:
        """
        Applies the training augmentation to a single image and its bounding boxes.
        
        Args:
            image: Input image as a numpy array (BGR).
            bboxes: List of YOLO format bboxes [[x_center, y_center, width, height], ...]
            class_labels: List of class indices.
            
        Returns:
            Tuple of (augmented_image, augmented_bboxes)
        """
        try:
            transformed = self.train_transform(image=image, bboxes=bboxes, class_labels=class_labels)
            return transformed['image'], transformed['bboxes']
        except Exception as e:
            logger.error(f"Augmentation failed: {e}")
            return image, bboxes

    def preprocess_for_inference(self, image: np.ndarray) -> np.ndarray:
        """
        Standardizes an image for model prediction (Resize and Normalization).
        """
        # OpenCV reads BGR, we ensure it's sized for the model
        image_resized = cv2.resize(image, (self.img_size, self.img_size))
        # Normalize pixel values to [0, 1]
        image_normalized = image_resized.astype(np.float32) / 255.0
        return image_normalized

if __name__ == "__main__":
    # Test block
    augmenter = CurrencyAugmenter(img_size=settings.IMG_SIZE)
    logger.info("Augmentation pipeline initialized.")
    
    # Dummy image for verification
    dummy_img = np.zeros((1000, 1000, 3), dtype=np.uint8)
    dummy_bboxes = [[0.5, 0.5, 0.2, 0.2]]
    dummy_labels = [0]
    
    aug_img, aug_boxes = augmenter.augment_image(dummy_img, dummy_bboxes, dummy_labels)
    logger.debug(f"Input shape: {dummy_img.shape} | Output shape: {aug_img.shape}")