# ==============================================================================
# Aviation Monitoring & Analytics Platform — Database Metadata Registry
# ==============================================================================
# Modul ini mengimpor seluruh model ORM deklaratif sehingga metadata tabel
# terdaftar lengkap di dalam Base.metadata untuk auto-generate Alembic migration.

from app.models.base import Base
from app.models.favorite import Favorite
from app.models.flight import Flight
from app.models.flight_observation import FlightObservation
from app.models.search_history import SearchHistory
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "Flight",
    "FlightObservation",
    "Favorite",
    "SearchHistory",
]
