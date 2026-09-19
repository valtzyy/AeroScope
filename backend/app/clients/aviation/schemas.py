# ==============================================================================
# Aviation Monitoring & Analytics Platform — Raw Aviationstack Schemas
# ==============================================================================
# Skema Pydantic untuk memvalidasi struktur JSON mentah dari Aviationstack API.
#
# Alasan Arsitektur:
# 1. Isolasi Kontrak Provider: Layer ini memvalidasi respons HTTP mentah dari Aviationstack.
# 2. Resiliensi Field Opsional: Banyak field seperti terminal, gate, baggage, dan koordinat live
#    bisa bernilai null pada respons Aviationstack tergantung jenis maskapai dan pelacakan radar.
#    Seluruh field tersebut didefinisikan sebagai Optional (default None).

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RawDeparture(BaseModel):
    airport: str | None = None
    timezone: str | None = None
    iata: str | None = None
    icao: str | None = None
    terminal: str | None = None
    gate: str | None = None
    delay: int | None = None
    scheduled: datetime | None = None
    estimated: datetime | None = None
    actual: datetime | None = None
    estimated_runway: datetime | None = None
    actual_runway: datetime | None = None

    model_config = ConfigDict(extra="ignore")


class RawArrival(BaseModel):
    airport: str | None = None
    timezone: str | None = None
    iata: str | None = None
    icao: str | None = None
    terminal: str | None = None
    gate: str | None = None
    baggage: str | None = None
    delay: int | None = None
    scheduled: datetime | None = None
    estimated: datetime | None = None
    actual: datetime | None = None
    estimated_runway: datetime | None = None
    actual_runway: datetime | None = None

    model_config = ConfigDict(extra="ignore")


class RawAirline(BaseModel):
    name: str | None = None
    iata: str | None = None
    icao: str | None = None

    model_config = ConfigDict(extra="ignore")


class RawFlightDesignator(BaseModel):
    number: str | None = None
    iata: str | None = None
    icao: str | None = None
    codeshared: dict | None = None

    model_config = ConfigDict(extra="ignore")


class RawAircraft(BaseModel):
    registration: str | None = None
    iata: str | None = None
    icao: str | None = None
    icao24: str | None = None

    model_config = ConfigDict(extra="ignore")


class RawLiveTelemetry(BaseModel):
    updated: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    altitude: float | None = None
    direction: float | None = None
    speed_horizontal: float | None = None
    speed_vertical: float | None = None
    is_ground: bool | None = None

    model_config = ConfigDict(extra="ignore")


class RawFlightItem(BaseModel):
    """Mewakili satu objek penerbangan pada daftar 'data' Aviationstack."""

    flight_date: str | None = None
    flight_status: str | None = None
    departure: RawDeparture | None = None
    arrival: RawArrival | None = None
    airline: RawAirline | None = None
    flight: RawFlightDesignator | None = None
    aircraft: RawAircraft | None = None
    live: RawLiveTelemetry | None = None

    model_config = ConfigDict(extra="ignore")


class RawPagination(BaseModel):
    limit: int = 100
    offset: int = 0
    count: int = 0
    total: int = 0

    model_config = ConfigDict(extra="ignore")


class RawAviationstackResponse(BaseModel):
    """Root response struktur endpoint /v1/flights Aviationstack."""

    pagination: RawPagination = Field(default_factory=RawPagination)
    data: list[RawFlightItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")
