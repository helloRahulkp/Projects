"""
Currency conversion service.
Uses open.er-api.com (free, no key required) with in-memory cache
and offline fallback rates.
"""
import time
import asyncio
from typing import Dict, Optional
import httpx

from backend.core.logger import logger

# Fallback rates relative to INR (updated periodically — used when API unreachable)
FALLBACK_RATES_FROM_INR: Dict[str, float] = {
    "INR": 1.0,
    "USD": 0.012,
    "EUR": 0.011,
    "GBP": 0.0095,
    "AED": 0.044,
    "SGD": 0.016,
    "JPY": 1.80,
}

_cache: Dict[str, Dict] = {}
_cache_time: Dict[str, float] = {}
CACHE_TTL = 3600  # 1 hour


class CurrencyService:
    BASE_URL = "https://open.er-api.com/v6/latest"

    async def get_rates(self, base: str = "INR") -> Dict[str, float]:
        """Fetch exchange rates for a base currency, with caching."""
        now = time.time()
        if base in _cache and (now - _cache_time.get(base, 0)) < CACHE_TTL:
            return _cache[base]

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.BASE_URL}/{base}")
                resp.raise_for_status()
                data = resp.json()
                rates = data.get("rates", {})
                _cache[base] = rates
                _cache_time[base] = now
                logger.info(f"Exchange rates refreshed for base={base}")
                return rates
        except Exception as e:
            logger.warning(f"Exchange rate fetch failed ({e}). Using fallback rates.")
            return self._fallback_rates(base)

    def _fallback_rates(self, base: str) -> Dict[str, float]:
        """Generate fallback rates by cross-multiplying through INR."""
        if base == "INR":
            return FALLBACK_RATES_FROM_INR.copy()
        inr_to_base = FALLBACK_RATES_FROM_INR.get(base, 1.0)
        return {
            curr: round(rate / inr_to_base, 6)
            for curr, rate in FALLBACK_RATES_FROM_INR.items()
        }

    async def convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> Dict:
        """Convert amount from one currency to another."""
        if from_currency == to_currency:
            return {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "original_amount": amount,
                "converted_amount": round(amount, 2),
                "rate": 1.0,
                "source": "identity",
            }

        rates = await self.get_rates(from_currency)
        rate = rates.get(to_currency)

        if rate is None:
            # Try inverse
            rates_inv = await self.get_rates(to_currency)
            inv_rate = rates_inv.get(from_currency)
            if inv_rate and inv_rate != 0:
                rate = 1.0 / inv_rate
            else:
                rate = 1.0

        converted = round(amount * rate, 2)
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "original_amount": amount,
            "converted_amount": converted,
            "rate": round(rate, 6),
            "source": "api" if from_currency in _cache else "fallback",
        }

    async def get_all_conversions(self, amount_inr: float, currencies: list) -> Dict:
        """Convert an INR amount to multiple target currencies."""
        results = {}
        for curr in currencies:
            result = await self.convert(amount_inr, "INR", curr)
            results[curr] = result
        return results


# Singleton
currency_service = CurrencyService()
