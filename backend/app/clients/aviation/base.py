# ==============================================================================
# Aviation Monitoring & Analytics Platform — Flight Data Provider Abstraction
# ==============================================================================
# Modul ini mendefinisikan interface abstrak (ABC) untuk penyedia data penerbangan
# serta Data Transfer Objects (DTO) internal domain aplikasi.
#
# Alasan Arsitektur:
# 1. Dependency Inversion Principle (DIP): Service layer bergantung pada abstraksi
#    FlightDataProvider, bukan pada implementasi konkret AviationstackClient.
# 2. Loose Coupling: Memungkinkan pengujian tanpa koneksi internet (MockFlightProvider)
#    atau penggantian ke penyedia lain (misal FlightAware/OpenSky) di masa depan
#    tanpa merombak kode bisnis aplikasi.

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FlightSearchQuery:
    """Parameter pencarian yang dinormalisasi untuk query penerbangan."""

    flight_iata: str | None = None
    airline_name: str | None = None
    dep_iata: str | None = None
    arr_iata: str | None = None
    flight_status: str | None = None
    flight_date: str | None = None
    page: int = 1
    limit: int = 20


@dataclass
class ObservationDTO:
    """Snapshot observasi telemetri penerbangan pada titik waktu tertentu."""

    status: str
    latitude: float | None = None
    longitude: float | None = None
    altitude: float | None = None
    speed: float | None = None
    observed_at: datetime | None = None


@dataclass
class FlightDTO:
    """Representasi data penerbangan yang telah dinormalisasi ke domain internal."""

    flight_number: str
    flight_date: str
    flight_status: str  # 'scheduled', 'active', 'landed', 'cancelled', 'incident', 'diverted'
    airline_name: str | None = None
    airline_iata: str | None = None
    airline_icao: str | None = None
    departure_airport: str | None = None
    departure_iata: str | None = None
    departure_icao: str | None = None
    departure_scheduled: datetime | None = None
    departure_actual: datetime | None = None
    departure_terminal: str | None = None
    departure_gate: str | None = None
    arrival_airport: str | None = None
    arrival_iata: str | None = None
    arrival_icao: str | None = None
    arrival_scheduled: datetime | None = None
    arrival_actual: datetime | None = None
    arrival_terminal: str | None = None
    arrival_gate: str | None = None
    arrival_baggage: str | None = None
    # Data telemetri snapshot terkini
    live_latitude: float | None = None
    live_longitude: float | None = None
    live_altitude: float | None = None
    live_speed: float | None = None
    last_observed_at: datetime | None = None


@dataclass
class FlightSearchResultDTO:
    """Hasil pencarian penerbangan disertai metadata paginasi."""

    items: list[FlightDTO] = field(default_factory=list)
    page: int = 1
    limit: int = 20
    total: int = 0


class FlightDataProvider(ABC):
    """
    Kontrak interface abstrak yang wajib diimplementasikan oleh setiap provider
    penerbangan (baik live Aviationstack maupun Mock fixture).
    """

    @abstractmethod
    async def search_flights(self, query: FlightSearchQuery) -> FlightSearchResultDTO:
        """Mencari penerbangan berdasarkan filter query yang diberikan."""
        pass

    @abstractmethod
    async def get_flight_by_identifier(
        self, flight_iata: str, flight_date: str | None = None
    ) -> FlightDTO | None:
        """Mengambil satu detail penerbangan berdasarkan nomor IATA dan tanggal opsional."""
        pass
