# ==============================================================================
# Unit Tests — Analytics & Flight Observations
# ==============================================================================
# Pengujian unit untuk validasi skema analitik terukur dan format observasi telemetri.

import uuid
from datetime import UTC, datetime

from app.schemas.analytics import (
    AirlineShare,
    AirportTraffic,
    AnalyticsOverviewResponse,
    ObservedDelayMetrics,
    StatusDistribution,
)
from app.schemas.observation import ObservationResponse


def test_status_distribution_defaults():
    """Memverifikasi seluruh status penerbangan memiliki nilai default 0."""
    dist = StatusDistribution()
    assert dist.scheduled == 0
    assert dist.active == 0
    assert dist.landed == 0
    assert dist.cancelled == 0


def test_observed_delay_metrics_calculation():
    """Memverifikasi format metrik keterlambatan terukur."""
    metrics = ObservedDelayMetrics(
        total_evaluated_flights=10,
        observed_on_time_rate_percent=90.0,
        observed_delayed_flights=1,
        observed_delay_rate_percent=10.0,
    )
    assert metrics.observed_on_time_rate_percent == 90.0
    assert metrics.observed_delayed_flights == 1


def test_analytics_overview_response_structure():
    """Memverifikasi struktur lengkap respon endpoint analitik dashboard."""
    overview = AnalyticsOverviewResponse(
        total_tracked_flights=50,
        status_distribution=StatusDistribution(active=15, scheduled=20, landed=15),
        delays=ObservedDelayMetrics(
            total_evaluated_flights=15,
            observed_on_time_rate_percent=86.7,
            observed_delayed_flights=2,
            observed_delay_rate_percent=4.0,
        ),
        top_airlines=[
            AirlineShare(airline_name="Garuda Indonesia", airline_iata="GA", flight_count=20, percentage_of_tracked=40.0),
        ],
        top_airports=[
            AirportTraffic(airport_iata="CGK", airport_name="Soekarno-Hatta", departures_count=15, arrivals_count=10),
        ],
    )
    assert overview.total_tracked_flights == 50
    assert len(overview.top_airlines) == 1
    assert "Statistik di atas dihitung berdasarkan sampel" in overview.data_scope_note


def test_observation_response_serialization():
    """Memverifikasi skema ObservationResponse untuk time-series telemetri."""
    obs = ObservationResponse(
        id=uuid.uuid4(),
        flight_id=uuid.uuid4(),
        status="active",
        latitude=-6.125,
        longitude=106.655,
        altitude=10500.0,
        speed=820.0,
        observed_at=datetime.now(UTC),
    )
    assert obs.altitude == 10500.0
    assert obs.status == "active"
