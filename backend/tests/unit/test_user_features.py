# ==============================================================================
# Unit Tests — User Features & Authorization
# ==============================================================================
# Pengujian unit untuk otorisasi RBAC (require_admin), ekstraksi token cookie,
# dan validasi skema favorit serta riwayat pencarian.

import uuid
from datetime import UTC, datetime

import pytest
from app.api.dependencies import require_admin
from app.core.exceptions import AuthorizationError
from app.models.user import User
from app.schemas.favorite import FavoriteCreateRequest
from app.schemas.search_history import SearchHistoryResponse


@pytest.mark.asyncio
async def test_require_admin_allows_admin_role():
    """Memverifikasi user dengan role 'ADMIN' diizinkan mengakses resource khusus."""
    admin_user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        password_hash="hash",
        name="Administrator",
        role="ADMIN",
    )
    result = await require_admin(current_user=admin_user)
    assert result.role == "ADMIN"


@pytest.mark.asyncio
async def test_require_admin_blocks_user_role():
    """Memverifikasi user dengan role 'USER' dilempar AuthorizationError (HTTP 403)."""
    regular_user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        password_hash="hash",
        name="Regular User",
        role="USER",
    )
    with pytest.raises(AuthorizationError) as exc_info:
        await require_admin(current_user=regular_user)
    assert "Administrator" in str(exc_info.value)


def test_favorite_create_schema_validation():
    """Memverifikasi skema FavoriteCreateRequest mewajibkan UUID yang valid."""
    valid_uuid = uuid.uuid4()
    req = FavoriteCreateRequest(flight_id=valid_uuid)
    assert req.flight_id == valid_uuid


def test_search_history_response_serialization():
    """Memverifikasi model SearchHistoryResponse dapat menserialisasi query_parameters JSON."""
    entry = SearchHistoryResponse(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        query_parameters={"dep_iata": "SFO", "arr_iata": "JFK", "status": "active"},
        result_count=5,
        searched_at=datetime.now(UTC),
    )
    assert entry.query_parameters["dep_iata"] == "SFO"
    assert entry.result_count == 5
