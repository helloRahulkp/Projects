"""
Constants for AI Currency Detection System.
"""
from typing import Dict, Tuple

# BGR colors for OpenCV visualization
CURRENCY_COLORS: Dict[str, Tuple[int, int, int]] = {
    "10_Old":  (118, 145, 175),
    "10_New":  (70, 110, 150),
    "20_Old":  (100, 180, 100),
    "20_New":  (0, 165, 255),
    "50_Old":  (230, 216, 173),
    "50_New":  (205, 150, 0),
    "100_Old": (180, 130, 110),
    "100_New": (130, 0, 75),
    "200":     (0, 140, 255),
    "500":     (128, 128, 128),
    "2000":    (120, 50, 150),
    "Unknown": (255, 255, 255),
}

DENOMINATION_VALUES: Dict[str, int] = {
    "10_Old": 10, "10_New": 10,
    "20_Old": 20, "20_New": 20,
    "50_Old": 50, "50_New": 50,
    "100_Old": 100, "100_New": 100,
    "200": 200, "500": 500, "2000": 2000,
}

# Multi-currency support metadata
CURRENCY_META = {
    "INR": {"symbol": "₹", "name": "Indian Rupee"},
    "USD": {"symbol": "$", "name": "US Dollar"},
    "EUR": {"symbol": "€", "name": "Euro"},
    "GBP": {"symbol": "£", "name": "British Pound"},
    "AED": {"symbol": "د.إ", "name": "UAE Dirham"},
    "SGD": {"symbol": "S$", "name": "Singapore Dollar"},
    "JPY": {"symbol": "¥", "name": "Japanese Yen"},
}

# Supported file formats
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]
SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv"]

IMG_SIZE = 640
MAX_DETECTIONS = 100

# Denomination display names (for TTS and UI)
DENOMINATION_DISPLAY: Dict[str, str] = {
    "10_Old": "10 Rupees", "10_New": "10 Rupees",
    "20_Old": "20 Rupees", "20_New": "20 Rupees",
    "50_Old": "50 Rupees", "50_New": "50 Rupees",
    "100_Old": "100 Rupees", "100_New": "100 Rupees",
    "200": "200 Rupees", "500": "500 Rupees", "2000": "2000 Rupees",
}

# Number words for TTS
NUMBER_WORDS = {
    10: "ten", 20: "twenty", 50: "fifty",
    100: "one hundred", 200: "two hundred",
    500: "five hundred", 2000: "two thousand",
}
