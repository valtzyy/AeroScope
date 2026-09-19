# ==============================================================================
# Aviation Monitoring & Analytics Platform — Health & Readiness Endpoints
# ==============================================================================
# Modul ini menyediakan pemeriksaan kesehatan aplikasi (Liveness & Readiness probe).
#
# Konsep DevOps & Observabilitas:
# 1. Liveness (/api/v1/health): Menandakan bahwa proses aplikasi FastAPI hidup
#    dan dapat merespons HTTP request. Jika endpoint ini gagal, container harus di-restart.
# 2. Readiness (/api/v1/health/ready): Menandakan bahwa aplikasi siap melayani traffic
#    karena seluruh dependency kritis (PostgreSQL & Redis) terhubung normal.
#    Jika database putus, endpoint mengembalikan status HTTP 503.

from typing import Any

import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import metrics
from app.db.session import get_db_session
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health & Monitoring"])


@router.get("", summary="Liveness Probe", status_code=status.HTTP_200_OK)
async def liveness_check() -> dict[str, Any]:
    """
    Pemeriksaan liveness sederhana untuk memverifikasi proses FastAPI berjalan.
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "provider": settings.FLIGHT_PROVIDER,
    }


@router.get("/ready", summary="Readiness Probe")
async def readiness_check(db: AsyncSession = Depends(get_db_session)) -> JSONResponse:
    """
    Pemeriksaan readiness komprehensif:
    1. Melakukan query 'SELECT 1' ke database PostgreSQL.
    2. Melakukan ping ke instance Redis.
    3. Menyertakan metrik operasional penggunaan provider eksternal.
    """
    checks: dict[str, str] = {}
    is_ready = True

    # 1. Verifikasi Database PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as exc:
        logger.error("Readiness check database gagal: %s", str(exc))
        checks["database"] = f"unhealthy: {str(exc)}"
        is_ready = False

    # 2. Verifikasi Cache Redis
    try:
        redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=2.0)
        await redis_client.ping()
        await redis_client.aclose()
        checks["redis"] = "healthy"
    except Exception as exc:
        logger.warning("Readiness check redis gagal: %s", str(exc))
        checks["redis"] = f"unhealthy: {str(exc)}"
        # Di lingkungan development, redis unhealthy masih dapat ditoleransi jika fallback tersedia,
        # namun di production status menjadi not ready.
        if settings.APP_ENV == "production":
            is_ready = False

    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
            "metrics": metrics.get_snapshot(),
        },
    )
