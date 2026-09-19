# ==============================================================================
# Unit Tests — Flight Data Provider Layer
# ==============================================================================
# Pengujian unit komprehensif untuk abstraksi provider, mapper, dan penanganan error.

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from app.clients.aviation.aviationstack import AviationstackProvider
from app.clients.aviation.base import FlightSearchQuery
from app.clients.aviation.exceptions import (
    ProviderAuthenticationError,
    ProviderQuotaExceededError,
)
from app.clients.aviation.mapper import map_raw_item_to_flight_dto, normalize_flight_status
from app.clients.aviation.mock_provider import MockFlightProvider
from app.clients.aviation.schemas import (
    RawAirline,
    RawArrival,
    RawDeparture,
    RawFlightDesignator,
    RawFlightItem,
    RawLiveTelemetry,
)


@pytest.mark.asyncio
async def test_mock_provider_search_and_pagination():
    """Memverifikasi MockFlightProvider dapat melakukan filter dan paginasi secara akurat."""
    provider = MockFlightProvider()

    # 1. Pencarian tanpa filter
    all_res = await provider.search_flights(FlightSearchQuery(page=1, limit=5))
    assert len(all_res.items) == 5
    assert all_res.total >= 7

    # 2. Filter berdasarkan flight IATA (case-insensitive substring)
    dl_res = await provider.search_flights(FlightSearchQuery(flight_iata="DL415"))
    assert len(dl_res.items) == 1
    assert dl_res.items[0].flight_number == "DL415"
    assert dl_res.items[0].departure_iata == "SFO"
    assert dl_res.items[0].arrival_iata == "JFK"

    # 3. Filter berdasarkan status penerbangan
    active_res = await provider.search_flights(FlightSearchQuery(flight_status="active"))
    assert all(f.flight_status == "active" for f in active_res.items)

    # 4. Pencarian detail berdasarkan identifier
    single = await provider.get_flight_by_identifier("GA404")
    assert single is not None
    assert single.airline_name == "Garuda Indonesia"


def test_mapper_normalization_and_optional_fields():
    """Memverifikasi mapper menormalisasi data mentah dan menangani field null dengan aman."""
    # Data mentah dengan sebagian field null
    raw_item = RawFlightItem(
        flight_date="2026-09-18",
        flight_status="ACTIVE",
        flight=RawFlightDesignator(iata="sq950", number="950"),
        airline=RawAirline(name="Singapore Airlines", iata="sq", icao="sia"),
        departure=RawDeparture(airport="Changi", iata="sin", terminal="3"),
        arrival=RawArrival(airport="Soekarno Hatta", iata="cgk"),
        live=RawLiveTelemetry(latitude=-1.12, longitude=104.8, altitude=8200.0, speed_horizontal=720.0),
    )

    dto = map_raw_item_to_flight_dto(raw_item)

    assert dto.flight_number == "SQ950"  # Uppercase
    assert dto.flight_status == "active"  # Lowercase
    assert dto.departure_iata == "SIN"
    assert dto.arrival_iata == "CGK"
    assert dto.departure_gate is None  # Handled gracefully as None
    assert dto.arrival_terminal is None
    assert dto.live_latitude == -1.12
    assert dto.live_altitude == 8200.0


def test_status_normalization_fallback():
    """Memverifikasi status tidak dikenal jatuh ke fallback 'scheduled'."""
    assert normalize_flight_status("UNKNOWN_XYZ") == "scheduled"
    assert normalize_flight_status(None) == "scheduled"
    assert normalize_flight_status("LANDED") == "landed"
    assert normalize_flight_status("cancelled") == "cancelled"


@pytest.mark.asyncio
async def test_aviationstack_quota_error_429():
    """Memverifikasi HTTP 429 dari Aviationstack langsung melempar ProviderQuotaExceededError tanpa retry."""
    provider = AviationstackProvider(api_key="dummy_test_key")

    mock_response = httpx.Response(
        status_code=429,
        json={"error": {"code": "rate_limit_reached", "message": "Usage limit exceeded"}},
        request=httpx.Request("GET", "http://test"),
    )

    with patch.object(httpx.AsyncClient, "get", AsyncMock(return_value=mock_response)) as mock_get:
        with pytest.raises(ProviderQuotaExceededError):
            await provider.search_flights(FlightSearchQuery())

        # Memastikan tidak ada retry pada error kuota 429
        assert mock_get.call_count == 1


@pytest.mark.asyncio
async def test_aviationstack_auth_error_401():
    """Memverifikasi HTTP 401 melempar ProviderAuthenticationError tanpa retry."""
    provider = AviationstackProvider(api_key="dummy_test_key")

    mock_response = httpx.Response(
        status_code=401,
        request=httpx.Request("GET", "http://test"),
    )

    with patch.object(httpx.AsyncClient, "get", AsyncMock(return_value=mock_response)) as mock_get:
        with pytest.raises(ProviderAuthenticationError):
            await provider.search_flights(FlightSearchQuery())

        # Memastikan tidak ada retry pada error otentikasi 401
        assert mock_get.call_count == 1
