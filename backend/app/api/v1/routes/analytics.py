# ==============================================================================
# Aviation Monitoring & Analytics Platform — Analytics Endpoints
# ==============================================================================
# Endpoint REST API untuk menyajikan ringkasan statistik dan metrik analitik dashboard.

from app.db.session import get_db_session
from app.schemas.analytics import AnalyticsOverviewResponse
from app.services.analytics_service import analytics_service
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/overview",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Ringkasan Statistik & Analisis Penerbangan Terlacak",
)
async def get_analytics_overview(
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Mengambil data agregat analitik: total penerbangan terlacak, distribusi status,
    tingkat ketepatan waktu terobservasi (Observed On-Time Rate), serta sebaran maskapai dan bandara.
    """
    overview: AnalyticsOverviewResponse = await analytics_service.get_overview(session=db)
    return {
        "data": overview,
        "meta": None,
        "error": None,
    }
