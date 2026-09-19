# ==============================================================================
# Aviation Monitoring & Analytics Platform — Search History Schemas
# ==============================================================================
# Skema Pydantic v2 untuk riwayat pencarian pengguna.

import uuid
from datetime import datetime

from app.schemas.flight import PaginationMeta
from pydantic import BaseModel, ConfigDict


class SearchHistoryResponse(BaseModel):
    """Respons satu entri riwayat pencarian."""

    id: uuid.UUID
    user_id: uuid.UUID
    query_parameters: dict
    result_count: int
    searched_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchHistoryListResponse(BaseModel):
    """Respons daftar riwayat pencarian berpaginasi."""

    data: list[SearchHistoryResponse]
    meta: PaginationMeta
    error: None = None
