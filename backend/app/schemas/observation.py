# ==============================================================================
# Aviation Monitoring & Analytics Platform — Flight Observation Schemas
# ==============================================================================
# Skema Pydantic v2 untuk serialisasi deret waktu observasi telemetri.

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ObservationResponse(BaseModel):
    """Satu titik observasi telemetri (waktu, koordinat, ketinggian, kecepatan)."""

    id: uuid.UUID
    flight_id: uuid.UUID
    status: str
    latitude: float | None = None
    longitude: float | None = None
    altitude: float | None = None
    speed: float | None = None
    observed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FlightObservationHistoryResponse(BaseModel):
    """Respons riwayat kumpulan titik observasi untuk suatu penerbangan."""

    flight_id: uuid.UUID
    total_observations: int
    observations: list[ObservationResponse]
