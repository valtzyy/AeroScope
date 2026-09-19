# ==============================================================================
# Aviation Monitoring & Analytics Platform — ORM Declarative Base & Mixins
# ==============================================================================
# Modul ini mendefinisikan Base class untuk SQLAlchemy 2.0 dan mixin umum.
#
# Alasan Arsitektur:
# 1. Penyimpanan UTC: Seluruh timestamp (created_at, updated_at, departure, arrival)
#    disimpan secara konsisten dalam format UTC di database.
#    Konversi ke zona waktu lokal pengguna hanya dilakukan pada layer presentasi (frontend).
# 2. Identitas UUID: Menggunakan UUID v4 sebagai primary key untuk mencegah enumeration attack
#    (IDOR) dan memudahkan replikasi data terdistribusi di masa depan.

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def get_utc_now() -> datetime:
    """Mengembalikan timestamp saat ini dalam zona waktu UTC."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """
    Kelas dasar deklaratif untuk seluruh entitas tabel SQLAlchemy.
    Menyediakan registri metadata terpusat untuk Alembic migration.
    """
    pass


class TimestampMixin:
    """
    Mixin yang secara otomatis menambahkan kolom pencatatan waktu standar
    ke setiap tabel turunan.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        nullable=False,
        comment="Waktu pencatatan entitas pertama kali (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False,
        comment="Waktu terakhir entitas diperbarui (UTC)",
    )


class UUIDPrimaryKeyMixin:
    """
    Mixin untuk kolom primary key bertipe UUID v4 acak.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Primary key UUID v4 unik global",
    )
