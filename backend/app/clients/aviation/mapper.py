# ==============================================================================
# Aviation Monitoring & Analytics Platform — Data Normalization Mapper
# ==============================================================================
# Fungsi-fungsi murni (pure functions) untuk memetakan respons JSON mentah Aviationstack
# ke dalam DTO domain internal aplikasi.
#
# Alasan Desain:
# 1. Isolasi Perubahan Eksternal: Jika Aviationstack mengubah nama field atau struktur nested,
#    hanya modul mapper ini yang perlu disesuaikan.
# 2. Sanitasi & Normalisasi: Membersihkan whitespace, standardisasi huruf besar (IATA/ICAO),
#    dan memastikan tanggal serta status penerbangan selalu seragam.

from datetime import UTC, datetime

from app.clients.aviation.base import FlightDTO, ObservationDTO
from app.clients.aviation.schemas import RawFlightItem


def normalize_flight_status(status_raw: str | None) -> str:
    """
    Menormalisasi status penerbangan menjadi salah satu nilai standar:
    'scheduled', 'active', 'landed', 'cancelled', 'incident', 'diverted'.
    """
    if not status_raw:
        return "scheduled"
    status_clean = status_raw.strip().lower()
    valid_statuses = {"scheduled", "active", "landed", "cancelled", "incident", "diverted"}
    return status_clean if status_clean in valid_statuses else "scheduled"


def map_raw_item_to_flight_dto(item: RawFlightItem) -> FlightDTO:
    """
    Mengonversi satu RawFlightItem dari Aviationstack menjadi FlightDTO internal domain.
    """
    # Menentukan nomor penerbangan IATA (misal DL415 atau AA100)
    flight_number = "UNKNOWN"
    if item.flight and item.flight.iata:
        flight_number = item.flight.iata.strip().upper()
    elif item.flight and item.flight.number:
        airline_code = (item.airline.iata or "") if item.airline else ""
        flight_number = f"{airline_code}{item.flight.number}".strip().upper()

    # Tanggal penerbangan (YYYY-MM-DD)
    flight_date = item.flight_date or datetime.now(UTC).strftime("%Y-%m-%d")

    # Status penerbangan yang sudah dinormalisasi
    flight_status = normalize_flight_status(item.flight_status)

    # Ekstraksi informasi keberangkatan (departure)
    dep = item.departure
    departure_airport = dep.airport if dep else None
    departure_iata = dep.iata.strip().upper() if dep and dep.iata else None
    departure_icao = dep.icao.strip().upper() if dep and dep.icao else None
    departure_scheduled = dep.scheduled if dep else None
    departure_actual = dep.actual if dep else None
    departure_terminal = dep.terminal if dep else None
    departure_gate = dep.gate if dep else None

    # Ekstraksi informasi kedatangan (arrival)
    arr = item.arrival
    arrival_airport = arr.airport if arr else None
    arrival_iata = arr.iata.strip().upper() if arr and arr.iata else None
    arrival_icao = arr.icao.strip().upper() if arr and arr.icao else None
    arrival_scheduled = arr.scheduled if arr else None
    arrival_actual = arr.actual if arr else None
    arrival_terminal = arr.terminal if arr else None
    arrival_gate = arr.gate if arr else None
    arrival_baggage = arr.baggage if arr else None

    # Ekstraksi maskapai (airline)
    airline_name = item.airline.name if item.airline else None
    airline_iata = item.airline.iata.strip().upper() if item.airline and item.airline.iata else None
    airline_icao = item.airline.icao.strip().upper() if item.airline and item.airline.icao else None

    # Ekstraksi telemetri live jika tersedia
    live = item.live
    live_latitude = live.latitude if live else None
    live_longitude = live.longitude if live else None
    live_altitude = live.altitude if live else None
    live_speed = live.speed_horizontal if live else None
    last_observed_at = live.updated if (live and live.updated) else datetime.now(UTC)

    return FlightDTO(
        flight_number=flight_number,
        flight_date=flight_date,
        flight_status=flight_status,
        airline_name=airline_name,
        airline_iata=airline_iata,
        airline_icao=airline_icao,
        departure_airport=departure_airport,
        departure_iata=departure_iata,
        departure_icao=departure_icao,
        departure_scheduled=departure_scheduled,
        departure_actual=departure_actual,
        departure_terminal=departure_terminal,
        departure_gate=departure_gate,
        arrival_airport=arrival_airport,
        arrival_iata=arrival_iata,
        arrival_icao=arrival_icao,
        arrival_scheduled=arrival_scheduled,
        arrival_actual=arrival_actual,
        arrival_terminal=arrival_terminal,
        arrival_gate=arrival_gate,
        arrival_baggage=arrival_baggage,
        live_latitude=live_latitude,
        live_longitude=live_longitude,
        live_altitude=live_altitude,
        live_speed=live_speed,
        last_observed_at=last_observed_at,
    )


def extract_observation_dto(dto: FlightDTO) -> ObservationDTO | None:
    """
    Mengekstrak snapshot observasi dari FlightDTO jika memiliki data status atau telemetri.
    """
    return ObservationDTO(
        status=dto.flight_status,
        latitude=dto.live_latitude,
        longitude=dto.live_longitude,
        altitude=dto.live_altitude,
        speed=dto.live_speed,
        observed_at=dto.last_observed_at or datetime.now(UTC),
    )
