# ==============================================================================
# Aviation Monitoring & Analytics Platform — Favorite Schemas
# ==============================================================================
# Skema Pydantic v2 untuk operasi favorit penerbangan pengguna.

import uuid
from datetime import datetime

from app.schemas.flight import FlightResponse
from pydantic import BaseModel, ConfigDict, Field


class FavoriteCreateRequest(BaseModel):
    """Permintaan untuk menambahkan penerbangan ke favorit."""

    flight_id: uuid.UUID = Field(description="ID UUID internal penerbangan yang ingin disimpan")


class FavoriteResponse(BaseModel):
    """Respons detail penerbangan favorit beserta metadata penerbangan lengkap."""

    id: uuid.UUID
    user_id: uuid.UUID
    flight_id: uuid.UUID
    created_at: datetime
    flight: FlightResponse | None = None

    model_config = ConfigDict(from_attributes=True)
