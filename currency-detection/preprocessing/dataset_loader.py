import os
import shutil
from pathlib import Path
from typing import List, Tuple

import cv2
from sklearn.model_selection import train_test_split
from src.core.config import settings
from src.core.logger import logger

class DatasetLoader:
    """
    Handles loading, auto-labeling (for detection), and splitting the Indian Currency dataset.
    Converts folder-based classification layouts into YOLOv8 detection formats.
    """

    def __init__(self):
        self.raw_dir = Path(settings.RAW_DATA_DIR)
        self.processed_dir = Path(settings.PROCESSED_DATA_DIR)
        self.split_ratios = {"train": 0.8, "val": 0.1, "test": 0.1}
        
        # Map folder names or versions to class index from constants/settings
        # Ensures mapping aligns perfectly with settings.CLASS_NAMES
        self.class_map = {name: idx for idx, name in enumerate(settings.CLASS_NAMES)}
        
        # Specific overrides just in case folder names are simple strings (e.g. "10", "100")
        # mapping them to corresponding class names in settings.CLASS_NAMES
        for idx, name in enumerate(settings.CLASS_NAMES):
            base_name = name.split("_")[0]  # turns "100_New" or "100_Old" into "100"
            if base_name not in self.class_map:
                self.class_map[base_name] = idx

        # Define internal structure for processed data
        for split in ["train", "val", "test"]:
            (self.processed_dir / split / "images").mkdir(parents=True, exist_ok=True)
            (self.processed_dir / split / "labels").mkdir(parents=True, exist_ok=True)

    def validate_and_get_data(self) -> List[Tuple[Path, int]]:
        """
        Scans the subdirectories, validates images, maps them to an index, 
        and flags them for split.
        """
        valid_items = []
        image_extensions = {".jpg", ".jpeg", ".png"}

        logger.info(f"Scanning raw folder: {self.raw_dir}")
        
        for img_path in self.raw_dir.rglob("*"):
            if img_path.suffix.lower() in image_extensions:
                # Find the denomination category from parent directory names
                folder_name = img_path.parent.name
                
                if folder_name in self.class_map:
                    class_idx = self.class_map[folder_name]
                    
                    # Validate image reading
                    img = cv2.imread(str(img_path))
                    if img is not None:
                        valid_items.append((img_path, class_idx))
                    else:
                        logger.warning(f"Skipping corrupted image: {img_path}")
                else:
                    logger.debug(f"Skipping directory category not mapped: {folder_name}")

        logger.info(f"Identified {len(valid_items)} total valid images across mapped denominations.")
        return valid_items

    def process_and_split(self):
        """Splits the elements, writes YOLO annotation text files, and saves them."""
        all_data = self.validate_and_get_data()
        
        if not all_data:
            logger.error("No data found to process! Please verify the files inside dataset/raw.")
            return

        # Split data: Train | (Val + Test)
        train_data, temp_data = train_test_split(
            all_data, train_size=self.split_ratios["train"], random_state=42
        )
        
        # Split data: Val | Test
        val_size_adj = self.split_ratios["val"] / (self.split_ratios["val"] + self.split_ratios["test"])
        val_data, test_data = train_test_split(
            temp_data, train_size=val_size_adj, random_state=42
        )

        self._write_and_move(train_data, "train")
        self._write_and_move(val_data, "val")
        self._write_and_move(test_data, "test")

        logger.info("Dataset structural conversion and splitting finished flawlessly!")

    def _write_and_move(self, data_list: List[Tuple[Path, int]], split_name: str):
        """Generates dynamic whole-image YOLO bounding boxes and copies files."""
        for img_path, class_idx in data_list:
            dest_img_name = img_path.name
            dest_label_name = img_path.with_suffix(".txt").name
            
            # Destination Paths
            img_dest = self.processed_dir / split_name / "images" / dest_img_name
            label_dest = self.processed_dir / split_name / "labels" / dest_label_name
            
            # Copy Image File
            shutil.copy2(img_path, img_dest)
            
            # Generate whole-image YOLO bounding box notation
            # Format: <class_index> <x_center> <y_center> <width> <height>
            # Center at (0.5, 0.5) spanning 1.0 of width and 1.0 of height
            yolo_box_string = f"{class_idx} 0.5 0.5 1.0 1.0\n"
            
            with open(label_dest, "w") as f:
                f.write(yolo_box_string)
                
        logger.info(f"Successfully compiled and moved {len(data_list)} assets into '{split_name}'.")

if __name__ == "__main__":
    loader = DatasetLoader()
    loader.process_and_split()
