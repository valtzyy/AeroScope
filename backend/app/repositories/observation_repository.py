# ==============================================================================
# Aviation Monitoring & Analytics Platform — Flight Observation Repository
# ==============================================================================
# Repositori operasi basis data untuk rekam jejak telemetri penerbangan.
#
# Alasan Arsitektur:
# Menggunakan kueri terindeks komposit (flight_id, observed_at) untuk mengambil
# data deret waktu (time-series) dengan urutan kronologis yang efisien.

import uuid
from datetime import UTC, datetime

from app.models.flight_observation import FlightObservation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ObservationRepository:
    """Mengelola pencatatan titik telemetri historis penerbangan."""

    @staticmethod
    async def record_observation(
        session: AsyncSession,
        flight_id: uuid.UUID,
        status: str,
        latitude: float | None = None,
        longitude: float | None = None,
        altitude: float | None = None,
        speed: float | None = None,
        observed_at: datetime | None = None,
    ) -> FlightObservation:
        """Menyimpan snapshot observasi telemetri baru ke database."""
        obs = FlightObservation(
            flight_id=flight_id,
            status=status,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            speed=speed,
            observed_at=observed_at or datetime.now(UTC),
        )
        session.add(obs)
        await session.flush()
        return obs

    @staticmethod
    async def get_flight_observations(
        session: AsyncSession, flight_id: uuid.UUID, limit: int = 50
    ) -> list[FlightObservation]:
        """
        Mengambil deret waktu observasi telemetri secara kronologis (ASC)
        untuk visualisasi grafik perubahan ketinggian dan kecepatan pesawat.
        """
        stmt = (
            select(FlightObservation)
            .where(FlightObservation.flight_id == flight_id)
            .order_by(FlightObservation.observed_at.asc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
