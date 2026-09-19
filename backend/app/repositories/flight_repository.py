# ==============================================================================
# Aviation Monitoring & Analytics Platform — Flight Repository
# ==============================================================================
# Layer repositori untuk operasi database entitas Flight menggunakan SQLAlchemy 2.0.
#
# Prinsip Keamanan & Desain:
# 1. Parameterized Queries: Seluruh kueri menggunakan objek Select dan parameter binding,
#    menghilangkan 100% risiko SQL Injection.
# 2. Idempotent Upsert: Memperbarui data penerbangan jika sudah ada atau menambah baru
#    tanpa menimbulkan error constraint duplikat.

import uuid

from app.clients.aviation.base import FlightDTO, FlightSearchQuery
from app.models.flight import Flight
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class FlightRepository:
    """Mengelola persistensi data penerbangan di database PostgreSQL."""

    @staticmethod
    async def get_by_id(session: AsyncSession, flight_id: uuid.UUID) -> Flight | None:
        """Mengambil data penerbangan berdasarkan primary key internal UUID."""
        stmt = select(Flight).where(Flight.id == flight_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_schedule(
        session: AsyncSession,
        flight_number: str,
        flight_date: str,
        dep_iata: str | None,
        arr_iata: str | None,
    ) -> Flight | None:
        """Mencari penerbangan berdasarkan nomor, tanggal, dan rute."""
        stmt = select(Flight).where(
            Flight.flight_number == flight_number.upper(),
            Flight.flight_date == flight_date,
            Flight.departure_iata == (dep_iata.upper() if dep_iata else None),
            Flight.arrival_iata == (arr_iata.upper() if arr_iata else None),
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_flight(session: AsyncSession, dto: FlightDTO) -> Flight:
        """
        Menyimpan data FlightDTO secara idempoten:
        Jika penerbangan sudah tercatat, perbarui status dan telemetri terkininya.
        Jika belum ada, buat baris data baru.
        """
        existing = await FlightRepository.get_by_schedule(
            session=session,
            flight_number=dto.flight_number,
            flight_date=dto.flight_date,
            dep_iata=dto.departure_iata,
            arr_iata=dto.arrival_iata,
        )

        if existing:
            # Perbarui kolom dengan data observasi terbaru
            existing.flight_status = dto.flight_status
            existing.departure_actual = dto.departure_actual or existing.departure_actual
            existing.arrival_actual = dto.arrival_actual or existing.arrival_actual
            existing.departure_terminal = dto.departure_terminal or existing.departure_terminal
            existing.departure_gate = dto.departure_gate or existing.departure_gate
            existing.arrival_terminal = dto.arrival_terminal or existing.arrival_terminal
            existing.arrival_gate = dto.arrival_gate or existing.arrival_gate
            existing.arrival_baggage = dto.arrival_baggage or existing.arrival_baggage
            existing.live_latitude = dto.live_latitude or existing.live_latitude
            existing.live_longitude = dto.live_longitude or existing.live_longitude
            existing.live_altitude = dto.live_altitude or existing.live_altitude
            existing.live_speed = dto.live_speed or existing.live_speed
            existing.last_observed_at = dto.last_observed_at or existing.last_observed_at
            return existing

        new_flight = Flight(
            flight_number=dto.flight_number.upper(),
            flight_date=dto.flight_date,
            flight_status=dto.flight_status,
            airline_name=dto.airline_name,
            airline_iata=dto.airline_iata,
            airline_icao=dto.airline_icao,
            departure_airport=dto.departure_airport,
            departure_iata=dto.departure_iata,
            departure_icao=dto.departure_icao,
            departure_scheduled=dto.departure_scheduled,
            departure_actual=dto.departure_actual,
            departure_terminal=dto.departure_terminal,
            departure_gate=dto.departure_gate,
            arrival_airport=dto.arrival_airport,
            arrival_iata=dto.arrival_iata,
            arrival_icao=dto.arrival_icao,
            arrival_scheduled=dto.arrival_scheduled,
            arrival_actual=dto.arrival_actual,
            arrival_terminal=dto.arrival_terminal,
            arrival_gate=dto.arrival_gate,
            arrival_baggage=dto.arrival_baggage,
            live_latitude=dto.live_latitude,
            live_longitude=dto.live_longitude,
            live_altitude=dto.live_altitude,
            live_speed=dto.live_speed,
            last_observed_at=dto.last_observed_at,
        )
        session.add(new_flight)
        await session.flush()  # Mengisi new_flight.id sebelum commit
        return new_flight

    @staticmethod
    async def list_flights(
        session: AsyncSession, query: FlightSearchQuery
    ) -> tuple[list[Flight], int]:
        """
        Mengambil daftar penerbangan dari database lokal dengan filter dan paginasi.
        Mengembalikan tuple (daftar_flight, total_count).
        """
        stmt = select(Flight)

        if query.flight_iata:
            stmt = stmt.where(Flight.flight_number.ilike(f"%{query.flight_iata.strip()}%"))
        if query.dep_iata:
            stmt = stmt.where(Flight.departure_iata == query.dep_iata.strip().upper())
        if query.arr_iata:
            stmt = stmt.where(Flight.arrival_iata == query.arr_iata.strip().upper())
        if query.flight_status:
            stmt = stmt.where(Flight.flight_status == query.flight_status.strip().lower())
        if query.flight_date:
            stmt = stmt.where(Flight.flight_date == query.flight_date.strip())

        # Hitung total hasil yang cocok
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await session.execute(count_stmt)).scalar() or 0

        # Paginasi dengan OFFSET dan LIMIT
        offset_val = (query.page - 1) * query.limit
        stmt = stmt.order_by(Flight.created_at.desc()).offset(offset_val).limit(query.limit)

        results = await session.execute(stmt)
        return list(results.scalars().all()), total
