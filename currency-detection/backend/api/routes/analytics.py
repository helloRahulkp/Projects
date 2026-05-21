"""
Analytics API routes.
"""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from backend.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/stats", summary="Get aggregate detection statistics")
async def get_stats():
    return analytics_service.get_stats()


@router.get("/history", summary="Get recent detection history")
async def get_history(limit: int = 50):
    return {"history": analytics_service.get_history(limit=limit)}


@router.get("/export/csv", summary="Export detection history as CSV")
async def export_csv():
    csv_data = analytics_service.export_csv()
    return PlainTextResponse(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=detection_history.csv"},
    )


@router.delete("/clear", summary="Clear detection history")
async def clear_history():
    analytics_service.clear()
    return {"success": True, "message": "History cleared."}
