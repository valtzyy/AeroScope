# ==============================================================================
# Aviation Monitoring & Analytics Platform — Flight API Schemas
# ==============================================================================
# Skema Pydantic v2 untuk validasi input query dan serialisasi respons endpoint penerbangan.
#
# Prinsip Desain API:
# 1. Nullable Fields Resilience: Field opsional seperti terminal, gate, baggage,
#    dan telemetri didefinisikan dengan jelas agar client/frontend dapat menampilkan
#    fallback yang elegan ("Not available").
# 2. Pemisahan ID Internal vs Eksternal: API mengembalikan UUID internal sebagai `id`,
#    sehingga client berinteraksi dengan identitas stabil sistem kita.

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaginationMeta(BaseModel):
    """Metadata penomoran halaman (paginasi)."""

    page: int = Field(ge=1, description="Nomor halaman saat ini")
    limit: int = Field(ge=1, le=100, description="Jumlah item per halaman")
    total: int = Field(ge=0, description="Total keseluruhan item")
    total_pages: int = Field(ge=0, description="Total keseluruhan halaman")


class FlightResponse(BaseModel):
    """Skema respons detail lengkap satu penerbangan."""

    id: uuid.UUID
    flight_number: str
    flight_date: str
    flight_status: str

    # Maskapai
    airline_name: str | None = None
    airline_iata: str | None = None
    airline_icao: str | None = None

    # Keberangkatan
    departure_airport: str | None = None
    departure_iata: str | None = None
    departure_icao: str | None = None
    departure_scheduled: datetime | None = None
    departure_actual: datetime | None = None
    departure_terminal: str | None = None
    departure_gate: str | None = None

    # Kedatangan
    arrival_airport: str | None = None
    arrival_iata: str | None = None
    arrival_icao: str | None = None
    arrival_scheduled: datetime | None = None
    arrival_actual: datetime | None = None
    arrival_terminal: str | None = None
    arrival_gate: str | None = None
    arrival_baggage: str | None = None

    # Telemetri live jika tersedia
    live_latitude: float | None = None
    live_longitude: float | None = None
    live_altitude: float | None = None
    live_speed: float | None = None
    last_observed_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FlightListResponse(BaseModel):
    """Format respons seragam untuk daftar pencarian penerbangan."""

    data: list[FlightResponse]
    meta: PaginationMeta
    error: None = None
