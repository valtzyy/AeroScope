# ==============================================================================
# Unit Tests — Health Endpoints
# ==============================================================================
# Pengujian unit untuk memverifikasi endpoint liveness dan root metadata.
# Unit test ini TIDAK memerlukan database eksternal atau Redis (murni in-memory).

import pytest
from app.main import create_app
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint():
    """Memverifikasi endpoint root '/' mengembalikan metadata aplikasi dan status provider."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Aviation Monitoring & Analytics" in data["name"]
        assert data["provider"] in ["mock", "aviationstack"]


@pytest.mark.asyncio
async def test_liveness_endpoint():
    """Memverifikasi endpoint liveness '/api/v1/health' mengembalikan status 200 ok."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "provider" in data
