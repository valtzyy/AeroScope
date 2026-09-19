# ==============================================================================
# Aviation Monitoring & Analytics Platform — Analytics Schemas
# ==============================================================================
# Skema Pydantic v2 untuk menyajikan metrik analitik dashboard yang jujur dan terukur.
#
# Alasan Desain Terminologi:
# 1. Menghindari Istilah Menyesatkan: Mengganti "Market Share" dengan "Tracked Flights by Airline"
#    dan "On-Time Rate" dengan "Observed On-Time Rate".
# 2. Lingkup Data: Seluruh metrik mencerminkan data penerbangan yang diobservasi dan tersimpan
#    dalam database aplikasi, bukan statistik universal industri penerbangan global.

from pydantic import BaseModel


class StatusDistribution(BaseModel):
    """Distribusi status penerbangan yang dilacak dalam database."""

    scheduled: int = 0
    active: int = 0
    landed: int = 0
    cancelled: int = 0
    incident: int = 0
    diverted: int = 0


class AirlineShare(BaseModel):
    """Sebaran penerbangan terlacak berdasarkan maskapai."""

    airline_name: str
    airline_iata: str | None = None
    flight_count: int
    percentage_of_tracked: float


class AirportTraffic(BaseModel):
    """Sebaran lalu lintas penerbangan terlacak berdasarkan bandara."""

    airport_iata: str
    airport_name: str | None = None
    departures_count: int
    arrivals_count: int


class ObservedDelayMetrics(BaseModel):
    """Tingkat ketepatan waktu dan keterlambatan berdasarkan penerbangan yang diobservasi."""

    total_evaluated_flights: int
    observed_on_time_rate_percent: float | None = None  # None jika belum ada penerbangan landed
    observed_delayed_flights: int
    observed_delay_rate_percent: float = 0.0


class AnalyticsOverviewResponse(BaseModel):
    """Data agregat komprehensif untuk halaman Dashboard Analitik."""

    total_tracked_flights: int
    status_distribution: StatusDistribution
    delays: ObservedDelayMetrics
    top_airlines: list[AirlineShare]
    top_airports: list[AirportTraffic]
    data_scope_note: str = (
        "Statistik di atas dihitung berdasarkan sampel penerbangan yang dilacak dan tersimpan "
        "di dalam sistem, bukan merupakan representasi kuota industri penerbangan global secara keseluruhan."
    )
