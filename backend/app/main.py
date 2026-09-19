# ==============================================================================
# Aviation Monitoring & Analytics Platform — Main FastAPI Application
# ==============================================================================
# Entry point utama aplikasi backend.
#
# Alasan Arsitektur & Keamanan:
# 1. Lifespan Events: Menggunakan context manager async 'lifespan' standar ASGI modern
#    untuk inisialisasi logger, validasi startup, dan graceful shutdown connection pool.
# 2. CORS Ketat: Mengizinkan domain frontend terdaftar (misal http://localhost:3000)
#    dengan allow_credentials=True agar browser mengizinkan cookie HttpOnly.
#    Wildcard '*' dilarang keras saat kredensial/cookie aktif.
# 3. Centralized Exception Handlers: Mencegah kebocoran traceback internal ke client.

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.db.session import engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Setup konfigurasi logging awal
setup_logging(level="DEBUG" if settings.DEBUG else "INFO")
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Mengelola siklus hidup (lifespan) aplikasi FastAPI:
    - STARTUP: Log inisialisasi dan verifikasi provider yang aktif.
    - SHUTDOWN: Membersihkan koneksi database connection pool secara anggun (graceful).
    """
    logger.info("==================================================")
    logger.info("Memulai %s", settings.APP_NAME)
    logger.info("Environment     : %s", settings.APP_ENV)
    logger.info("Flight Provider : %s", settings.FLIGHT_PROVIDER)
    logger.info("==================================================")

    yield  # Aplikasi berjalan dan melayani request

    logger.info("Menghentikan aplikasi dan menutup connection pool database...")
    await engine.dispose()
    logger.info("Siklus shutdown selesai dengan aman.")


def create_app() -> FastAPI:
    """
    Application Factory untuk membuat instance FastAPI.
    Pendekatan factory mempermudah pembuatan instance baru saat automated testing.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description=(
            "REST API Backend untuk Aviation Monitoring & Analytics Platform. "
            "Mengintegrasikan data penerbangan dari Aviationstack dengan caching, "
            "keamanan berbasis cookie, dan observabilitas operasional."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. Konfigurasi Keamanan CORS (Cross-Origin Resource Sharing)
    # allow_credentials=True krusial agar browser dapat mengirim & menerima cookie HttpOnly
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 2. Daftarkan Centralized Exception Handlers
    register_exception_handlers(app)

    # 3. Integrasi Slowapi Rate Limiter
    from app.core.rate_limit import limiter
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # 4. Daftarkan Router Master API v1
    app.include_router(api_v1_router)

    # 4. Root Endpoint Informatif
    @app.get("/", summary="Root Metadata Endpoint", tags=["Root"])
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health",
            "provider": settings.FLIGHT_PROVIDER,
        }

    return app


# Instance aplikasi default untuk uvicorn ASGI runner
app = create_app()
