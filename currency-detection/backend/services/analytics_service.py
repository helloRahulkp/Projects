"""
Analytics service — tracks detection history in memory and on disk (JSON).
Provides aggregation for the dashboard.
"""
import json
import os
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from backend.core.logger import logger

HISTORY_FILE = Path("outputs/reports/detection_history.json")


class AnalyticsService:
    def __init__(self):
        self._history: List[Dict] = []
        self._load()

    def _load(self):
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
        except Exception as e:
            logger.warning(f"Analytics load failed: {e}")
            self._history = []

    def _save(self):
        try:
            HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self._history[-500:], f, indent=2)  # keep last 500
        except Exception as e:
            logger.warning(f"Analytics save failed: {e}")

    def record(self, results: Dict, source: str = "image"):
        """Record a detection event."""
        entry = {
            "id": int(time.time() * 1000),
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "total_amount": results.get("total_amount", 0),
            "total_count": results.get("total_count", 0),
            "summary": results.get("summary", {}),
            "currency": results.get("currency", "INR"),
        }
        self._history.append(entry)
        self._save()
        return entry

    def get_history(self, limit: int = 50) -> List[Dict]:
        return self._history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        if not self._history:
            return {"total_sessions": 0, "total_amount_detected": 0,
                    "denomination_counts": {}, "recent_trend": []}

        total_amount = sum(e["total_amount"] for e in self._history)
        denom_counts: Dict[str, int] = defaultdict(int)
        for entry in self._history:
            for k, v in entry.get("summary", {}).items():
                denom_counts[k] += v

        # Last 10 for trend chart
        trend = [
            {"timestamp": e["timestamp"], "amount": e["total_amount"]}
            for e in self._history[-10:]
        ]

        return {
            "total_sessions": len(self._history),
            "total_amount_detected": total_amount,
            "avg_amount_per_session": round(total_amount / len(self._history), 2),
            "denomination_counts": dict(denom_counts),
            "recent_trend": trend,
        }

    def export_csv(self) -> str:
        """Return CSV string of history."""
        lines = ["timestamp,source,total_amount,total_count,currency"]
        for e in self._history:
            lines.append(
                f"{e['timestamp']},{e['source']},{e['total_amount']},"
                f"{e['total_count']},{e['currency']}"
            )
        return "\n".join(lines)

    def clear(self):
        self._history = []
        self._save()


analytics_service = AnalyticsService()
