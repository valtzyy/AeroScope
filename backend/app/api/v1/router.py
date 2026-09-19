# ==============================================================================
# Aviation Monitoring & Analytics Platform — Master v1 API Router
# ==============================================================================
# Modul ini mengumpulkan seluruh sub-router untuk API versi 1 (/api/v1).

from app.api.v1.routes import analytics, auth, favorites, flights, health, search_history
from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/api/v1")

# Mendaftarkan seluruh sub-router ke router master
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(flights.router)
api_v1_router.include_router(favorites.router)
api_v1_router.include_router(search_history.router)
api_v1_router.include_router(analytics.router)
