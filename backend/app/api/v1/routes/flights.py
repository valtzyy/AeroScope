# ==============================================================================
# Aviation Monitoring & Analytics Platform — Flight Endpoints
# ==============================================================================
# Endpoint REST API untuk pencarian, detail, dan refresh data penerbangan.
#
# Alasan Desain & Keamanan:
# 1. Validasi Input Ketat: Menggunakan Query constraints (regex untuk kode IATA bandara,
#    ge=1 dan le=100 untuk limit paginasi) untuk mencegah request abusif.
# 2. Respon Konsisten: Seluruh data dikembalikan dalam struktur { "data": ..., "meta": ..., "error": null }.

import uuid
from typing import Annotated

from app.clients.aviation.base import FlightSearchQuery
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db_session
from app.schemas.flight import FlightListResponse
from app.services.flight_service import flight_service
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.get(
    "",
    response_model=FlightListResponse,
    summary="Pencarian & Filtering Penerbangan",
    status_code=status.HTTP_200_OK,
)
@limiter.limit(f"{settings.RATE_LIMIT_SEARCH_PER_MINUTE}/minute")
async def search_flights(
    request: Request,
    flight_number: Annotated[str | None, Query(description="Nomor penerbangan IATA (misal DL415)")] = None,
    airline: Annotated[str | None, Query(description="Nama maskapai (misal Delta)")] = None,
    dep_iata: Annotated[str | None, Query(description="Kode IATA bandara asal (misal SFO)", max_length=5)] = None,
    arr_iata: Annotated[str | None, Query(description="Kode IATA bandara tujuan (misal JFK)", max_length=5)] = None,
    flight_status: Annotated[str | None, Query(description="Status: scheduled, active, landed, cancelled")] = None,
    date: Annotated[str | None, Query(description="Tanggal penerbangan format YYYY-MM-DD")] = None,
    page: Annotated[int, Query(ge=1, description="Nomor halaman paginasi")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Jumlah penerbangan per halaman")] = 20,
    db: AsyncSession = Depends(get_db_session),
) -> FlightListResponse:
    """
    Mencari daftar penerbangan berdasarkan kriteria filter dengan paginasi.
    Data disajikan melalui lapisan Cache Redis dengan fallback ke provider eksternal.
    """
    query = FlightSearchQuery(
        flight_iata=flight_number,
        airline_name=airline,
        dep_iata=dep_iata,
        arr_iata=arr_iata,
        flight_status=flight_status,
        flight_date=date,
        page=page,
        limit=limit,
    )
    return await flight_service.search_flights(session=db, query=query)


@router.get(
    "/{flight_id}",
    response_model=dict,
    summary="Detail Lengkap Penerbangan",
    status_code=status.HTTP_200_OK,
)
async def get_flight_detail(
    flight_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Mengambil data detail lengkap satu penerbangan berdasarkan internal UUID.
    """
    flight = await flight_service.get_flight_by_id(session=db, flight_id=flight_id)
    return {
        "data": flight,
        "meta": None,
        "error": None,
    }


@router.post(
    "/{flight_id}/refresh",
    response_model=dict,
    summary="Refresh Status Penerbangan Manual",
    status_code=status.HTTP_200_OK,
)
@limiter.limit(f"{settings.RATE_LIMIT_REFRESH_PER_MINUTE}/minute")
async def refresh_flight(
    request: Request,
    flight_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Menyinkronkan status terkini dan telemetri penerbangan secara langsung dari provider.
    Dibatasi dengan rate limiting untuk menghemat kuota request upstream.
    """
    updated_flight = await flight_service.refresh_flight_status(session=db, flight_id=flight_id)
    return {
        "data": updated_flight,
        "meta": None,
        "error": None,
    }


@router.get(
    "/{flight_id}/observations",
    response_model=dict,
    summary="Riwayat Observasi Telemetri Penerbangan",
    status_code=status.HTTP_200_OK,
)
async def get_flight_observations_timeline(
    flight_id: uuid.UUID,
    limit: Annotated[int, Query(ge=1, le=100, description="Jumlah titik observasi")] = 50,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Mengambil deret waktu observasi telemetri (koordinat, ketinggian, kecepatan)
    untuk visualisasi grafik penerbangan secara kronologis.
    """
    from app.schemas.observation import ObservationResponse
    observations = await flight_service.get_flight_observations(session=db, flight_id=flight_id, limit=limit)
    return {
        "data": [ObservationResponse.model_validate(obs) for obs in observations],
        "meta": {"total": len(observations)},
        "error": None,
    }

