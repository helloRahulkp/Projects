"""
Unit tests for AI Currency Detection System v2.0
Run: pytest tests/ -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from unittest.mock import patch, MagicMock


# ── Core Config Tests ─────────────────────────────────────────────────────────
class TestConfig:
    def test_settings_import(self):
        from backend.core.config import settings
        assert settings.VERSION == "2.0.0"
        assert settings.CONFIDENCE_THRESHOLD > 0
        assert len(settings.CLASS_NAMES) == 11

    def test_denomination_map_completeness(self):
        from backend.core.config import settings
        for cls in settings.CLASS_NAMES:
            assert cls in settings.DENOMINATION_MAP, f"{cls} missing from DENOMINATION_MAP"

    def test_device_detection(self):
        from backend.core.config import detect_device
        device = detect_device()
        assert device in ("cpu", "cuda", "mps")


# ── Constants Tests ────────────────────────────────────────────────────────────
class TestConstants:
    def test_currency_colors_complete(self):
        from backend.core.constants import CURRENCY_COLORS
        from backend.core.config import settings
        for cls in settings.CLASS_NAMES:
            assert cls in CURRENCY_COLORS, f"No color for {cls}"

    def test_denomination_values(self):
        from backend.core.constants import DENOMINATION_VALUES
        assert DENOMINATION_VALUES["500"] == 500
        assert DENOMINATION_VALUES["2000"] == 2000
        assert DENOMINATION_VALUES["10_Old"] == 10
        assert DENOMINATION_VALUES["10_New"] == 10


# ── TTS Service Tests ─────────────────────────────────────────────────────────
class TestTTSService:
    def test_build_detection_speech_empty(self):
        from backend.services.tts_service import build_detection_speech
        result = build_detection_speech([], 0)
        assert "No currency" in result

    def test_build_detection_speech_single(self):
        from backend.services.tts_service import build_detection_speech
        dets = [{"denomination": 500}]
        result = build_detection_speech(dets, 500)
        assert "500" in result or "five hundred" in result.lower()
        assert "500" in result or "rupee" in result.lower()

    def test_build_detection_speech_multiple(self):
        from backend.services.tts_service import build_detection_speech
        dets = [{"denomination": 100}, {"denomination": 500}]
        result = build_detection_speech(dets, 600)
        assert len(result) > 10


# ── Analytics Service Tests ───────────────────────────────────────────────────
class TestAnalyticsService:
    def test_record_and_stats(self):
        from backend.services.analytics_service import AnalyticsService
        svc = AnalyticsService()
        svc.clear()

        sample = {
            "total_amount": 500,
            "total_count": 1,
            "summary": {"500": 1},
            "currency": "INR",
        }
        svc.record(sample, source="test")
        stats = svc.get_stats()
        assert stats["total_sessions"] >= 1
        assert stats["total_amount_detected"] >= 500

    def test_export_csv(self):
        from backend.services.analytics_service import AnalyticsService
        svc = AnalyticsService()
        csv = svc.export_csv()
        assert "timestamp" in csv
        assert "total_amount" in csv

    def test_clear(self):
        from backend.services.analytics_service import AnalyticsService
        svc = AnalyticsService()
        svc.record({"total_amount": 100, "total_count": 1, "summary": {}, "currency": "INR"})
        svc.clear()
        assert len(svc.get_history()) == 0


# ── Currency Service Tests ────────────────────────────────────────────────────
class TestCurrencyService:
    @pytest.mark.asyncio
    async def test_fallback_rates(self):
        from backend.services.currency_service import CurrencyService
        svc = CurrencyService()
        rates = svc._fallback_rates("INR")
        assert "USD" in rates
        assert "EUR" in rates
        assert rates["INR"] == 1.0

    @pytest.mark.asyncio
    async def test_convert_same_currency(self):
        from backend.services.currency_service import CurrencyService
        svc = CurrencyService()
        result = await svc.convert(500, "INR", "INR")
        assert result["converted_amount"] == 500
        assert result["rate"] == 1.0


# ── Denomination Counter Tests ─────────────────────────────────────────────────
class TestDenominationCounter:
    def test_total_calculation(self):
        from backend.core.constants import DENOMINATION_VALUES
        notes = ["500", "500", "100_New", "200"]
        total = sum(DENOMINATION_VALUES[n] for n in notes)
        assert total == 1300

    def test_summary_aggregation(self):
        summary = {}
        labels = ["500", "500", "100_New", "200", "500"]
        for label in labels:
            summary[label] = summary.get(label, 0) + 1
        assert summary["500"] == 3
        assert summary["100_New"] == 1


# ── Image Detector Tests (mocked) ─────────────────────────────────────────────
class TestImageDetectorMocked:
    def test_dummy_image_returns_structure(self):
        """Test that the result structure is correct using a zero image."""
        with patch("ultralytics.YOLO") as MockYOLO:
            mock_result = MagicMock()
            mock_result.boxes = []
            MockYOLO.return_value.predict.return_value = [mock_result]

            from backend.detection.detect_image import ImageDetector
            # Reset singleton for test
            ImageDetector._instance = None
            detector = ImageDetector.__new__(ImageDetector)
            detector._initialized = False
            detector.model_path = "models/checkpoints/best.pt"
            detector.device = "cpu"
            detector.model = MockYOLO.return_value
            detector._initialized = True

            dummy = np.zeros((640, 640, 3), dtype=np.uint8)
            result = detector.process_image(dummy)

            assert "detections" in result
            assert "summary" in result
            assert "total_amount" in result
            assert "total_count" in result
            assert result["currency"] == "INR"
            assert result["total_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
