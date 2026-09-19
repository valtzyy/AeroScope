# ==============================================================================
# Aviation Monitoring & Analytics Platform — Flight Provider Factory
# ==============================================================================
# Modul ini menyediakan fungsi factory untuk menginstansiasi implementasi
# FlightDataProvider yang sesuai berdasarkan konfigurasi FLIGHT_PROVIDER.

from app.clients.aviation.aviationstack import AviationstackProvider
from app.clients.aviation.base import FlightDataProvider
from app.clients.aviation.mock_provider import MockFlightProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_flight_provider() -> FlightDataProvider:
    """
    Factory function untuk mendapatkan instance provider aktif.
    - 'mock': Menggunakan MockFlightProvider (fixture offline).
    - 'aviationstack': Menggunakan AviationstackProvider (koneksi live ke API).
    """
    if settings.FLIGHT_PROVIDER == "aviationstack":
        return AviationstackProvider(
            api_key=settings.AVIATIONSTACK_API_KEY,
            base_url=settings.AVIATIONSTACK_BASE_URL,
            timeout=settings.AVIATIONSTACK_TIMEOUT_SECONDS,
        )
    return MockFlightProvider()
