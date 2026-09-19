# ==============================================================================
# Aviation Monitoring & Analytics Platform — Database Engine & Session
# ==============================================================================
# Modul ini mengelola koneksi asynchronous ke database PostgreSQL menggunakan
# SQLAlchemy 2.0 dan driver asyncpg.
#
# Alasan Arsitektur & Best Practices:
# 1. Connection Pooling: Engine mengelola pool koneksi (pool_size=10, max_overflow=20)
#    untuk menghemat resource pembuatan koneksi TCP baru pada setiap request HTTP.
# 2. pool_pre_ping=True: Secara otomatis menguji koneksi (SELECT 1) sebelum diserahkan
#    ke request, mencegah error 'stale/dropped connection' jika database sempat terputus.
# 3. Contextual Lifecycle: Dependency `get_db_session` menjamin sesi selalu di-close
#    dan perubahan di-commit/rollback secara aman pada akhir lifecycle request.

from collections.abc import AsyncGenerator

from app.core.config import settings
from app.core.logging import get_logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = get_logger(__name__)

# Membuat async engine dengan connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800,  # Daur ulang koneksi setiap 30 menit
)

# Factory sessionmaker asynchronous
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """
    FastAPI dependency yang menyediakan sesi database terisolasi untuk setiap request.
    Otomatis melakukan rollback jika terjadi exception di route handler,
    dan menutup (close) sesi saat request selesai.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
