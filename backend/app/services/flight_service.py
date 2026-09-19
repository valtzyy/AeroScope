# ==============================================================================
# Aviation Monitoring & Analytics Platform — Flight Service Layer
# ==============================================================================
# Service layer yang mengorkestrasi logika bisnis pencarian, caching, dan persistensi penerbangan.
#
# Alasan Arsitektur & Aliran Data:
# 1. Aliran Request:
#    Browser -> FastAPI Route -> FlightService -> CacheService (Redis)
#                                               -> (Jika Miss) FlightDataProvider (Aviationstack/Mock)
#                                               -> Persistensi ke FlightRepository (PostgreSQL)
#                                               -> Simpan ke Cache dengan dynamic TTL
#                                               -> Kembalikan ke Client
# 2. Quota Protection: Alur ini secara dramatis memangkas jumlah request ke Aviationstack
#    karena pencarian serupa akan disajikan dari cache memori dalam hitungan milidetik.

import math
import uuid

from app.clients.aviation.base import (
    FlightDataProvider,
    FlightSearchQuery,
)
from app.clients.aviation.factory import get_flight_provider
from app.core.exceptions import ResourceNotFoundError
from app.core.logging import get_logger
from app.models.flight import Flight
from app.repositories.flight_repository import FlightRepository
from app.schemas.flight import FlightListResponse, FlightResponse, PaginationMeta
from app.services.cache_service import (
    build_flight_search_cache_key,
    cache_service,
    calculate_ttl_for_status,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class FlightService:
    """Mengelola alur bisnis penerbangan: cache-aside, sinkronisasi provider, dan database."""

    def __init__(self, provider: FlightDataProvider | None = None):
        self.provider = provider or get_flight_provider()

    async def search_flights(
        self, session: AsyncSession, query: FlightSearchQuery
    ) -> FlightListResponse:
        """
        Mencari penerbangan dengan pola cache-aside:
        1. Cek Redis menggunakan normalized query hash.
        2. Jika ada (cache hit), langsung deserialisasi dan kembalikan.
        3. Jika tidak ada (cache miss), ambil dari provider, simpan ke database,
           simpan ke cache dengan TTL dinamis, lalu kembalikan hasilnya.
        """
        cache_key = build_flight_search_cache_key(query)

        # 1. Cek Cache Ephemeral
        cached_payload = await cache_service.get(cache_key)
        if cached_payload:
            logger.debug("Cache HIT untuk query: %s", cache_key)
            return FlightListResponse.model_validate(cached_payload)

        logger.debug("Cache MISS untuk query: %s. Mengambil dari provider...", cache_key)

        # 2. Ambil data dari provider eksternal (Aviationstack atau Mock)
        provider_result = await self.provider.search_flights(query)

        # 3. Persistensi idempoten ke database PostgreSQL dan pencatatan snapshot observasi
        persisted_flights: list[Flight] = []
        for item_dto in provider_result.items:
            saved_flight = await FlightRepository.upsert_flight(session, item_dto)
            persisted_flights.append(saved_flight)

            # Catat snapshot historis telemetri jika data status atau koordinat tersedia
            from app.repositories.observation_repository import ObservationRepository
            await ObservationRepository.record_observation(
                session=session,
                flight_id=saved_flight.id,
                status=saved_flight.flight_status,
                latitude=saved_flight.live_latitude,
                longitude=saved_flight.live_longitude,
                altitude=saved_flight.live_altitude,
                speed=saved_flight.live_speed,
                observed_at=saved_flight.last_observed_at,
            )

        # 4. Susun respons data dan metadata paginasi
        total_items = provider_result.total
        total_pages = math.ceil(total_items / query.limit) if total_items > 0 else 0

        flight_responses = [FlightResponse.model_validate(f) for f in persisted_flights]
        response_data = FlightListResponse(
            data=flight_responses,
            meta=PaginationMeta(
                page=query.page,
                limit=query.limit,
                total=total_items,
                total_pages=total_pages,
            ),
        )

        # 5. Tentukan TTL dinamis berdasarkan status item pertama (atau default)
        sample_status = persisted_flights[0].flight_status if persisted_flights else None
        ttl_seconds = calculate_ttl_for_status(sample_status)

        # Simpan ke cache
        await cache_service.set(cache_key, response_data.model_dump(mode="json"), ttl_seconds=ttl_seconds)

        return response_data

    async def get_flight_by_id(self, session: AsyncSession, flight_id: uuid.UUID) -> FlightResponse:
        """Mengambil detail satu penerbangan berdasarkan internal UUID."""
        flight = await FlightRepository.get_by_id(session, flight_id)
        if not flight:
            raise ResourceNotFoundError(f"Penerbangan dengan ID {flight_id} tidak ditemukan.")
        return FlightResponse.model_validate(flight)

    async def refresh_flight_status(
        self, session: AsyncSession, flight_id: uuid.UUID
    ) -> FlightResponse:
        """
        Melakukan sinkronisasi manual status penerbangan terkini dari provider.
        Hanya dipanggil secara eksplisit (rate-limited) untuk menghemat kuota.
        """
        flight = await FlightRepository.get_by_id(session, flight_id)
        if not flight:
            raise ResourceNotFoundError(f"Penerbangan dengan ID {flight_id} tidak ditemukan.")

        # Ambil status terbaru dari provider menggunakan nomor penerbangan dan tanggal
        latest_dto = await self.provider.get_flight_by_identifier(
            flight_iata=flight.flight_number, flight_date=flight.flight_date
        )

        if latest_dto:
            updated_flight = await FlightRepository.upsert_flight(session, latest_dto)
            # Catat observasi baru saat refresh manual
            from app.repositories.observation_repository import ObservationRepository
            await ObservationRepository.record_observation(
                session=session,
                flight_id=updated_flight.id,
                status=updated_flight.flight_status,
                latitude=updated_flight.live_latitude,
                longitude=updated_flight.live_longitude,
                altitude=updated_flight.live_altitude,
                speed=updated_flight.live_speed,
                observed_at=updated_flight.last_observed_at,
            )
            return FlightResponse.model_validate(updated_flight)

        return FlightResponse.model_validate(flight)

    async def get_flight_observations(
        self, session: AsyncSession, flight_id: uuid.UUID, limit: int = 50
    ) -> list:
        """Mengambil rekam jejak telemetri historis suatu penerbangan."""
        flight = await FlightRepository.get_by_id(session, flight_id)
        if not flight:
            raise ResourceNotFoundError(f"Penerbangan dengan ID {flight_id} tidak ditemukan.")

        from app.repositories.observation_repository import ObservationRepository
        observations = await ObservationRepository.get_flight_observations(session, flight_id, limit)
        return observations


# Inisialisasi default FlightService
flight_service = FlightService()
