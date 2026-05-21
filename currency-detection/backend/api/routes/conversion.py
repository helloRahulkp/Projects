"""
Currency conversion API routes.
"""
from fastapi import APIRouter, HTTPException, Query
from backend.services.currency_service import currency_service
from backend.core.constants import CURRENCY_META

router = APIRouter()

SUPPORTED = list(CURRENCY_META.keys())


@router.get("/rates", summary="Get live exchange rates from INR")
async def get_rates(base: str = Query("INR", description="Base currency")):
    base = base.upper()
    rates = await currency_service.get_rates(base)
    # Filter to only return supported currencies
    filtered = {k: v for k, v in rates.items() if k in SUPPORTED}
    return {"base": base, "rates": filtered, "supported_currencies": CURRENCY_META}


@router.get("/convert", summary="Convert amount between currencies")
async def convert(
    amount: float = Query(..., gt=0),
    from_currency: str = Query("INR"),
    to_currency: str = Query("USD"),
):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    result = await currency_service.convert(amount, from_currency, to_currency)
    return result


@router.post("/convert-all", summary="Convert INR amount to all supported currencies")
async def convert_all(payload: dict):
    amount = payload.get("amount", 0)
    currencies = payload.get("currencies", ["USD", "EUR", "GBP", "AED", "SGD"])
    if amount <= 0:
        raise HTTPException(400, detail="Amount must be positive.")
    results = await currency_service.get_all_conversions(amount, currencies)
    return {
        "base_amount": amount,
        "base_currency": "INR",
        "conversions": results,
    }
