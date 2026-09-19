# ==============================================================================
# Aviation Monitoring & Analytics Platform — Alembic Migration Environment
# ==============================================================================
# Modul ini dieksekusi oleh Alembic saat menjalankan 'alembic upgrade' atau
# 'alembic revision --autogenerate'.
#
# Alasan Arsitektur:
# 1. Menggunakan metadata terpusat dari Base.metadata agar seluruh tabel terdeteksi.
# 2. URL database dibaca langsung dari Settings aplikasi (app.core.config),
#    sehingga tidak ada duplikasi string koneksi.

import asyncio
from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.db.base import Base

# Konfigurasi logging dari alembic.ini
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Registri metadata model untuk autogenerate migrasi
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Menjalankan migrasi dalam mode 'offline' (menghasilkan script SQL tanpa koneksi aktif).
    """
    # Mengonversi skema asyncpg menjadi standar postgresql untuk mode offline jika perlu
    url = settings.DATABASE_URL.replace("+asyncpg", "")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Menjalankan migrasi dalam mode 'online' menggunakan async engine asyncpg.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
