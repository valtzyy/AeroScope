# ==============================================================================
# Aviation Monitoring & Analytics Platform — Favorite ORM Model
# ==============================================================================
# Model database relasional untuk fitur penerbangan favorit yang disimpan pengguna.
#
# Alasan Desain & Keamanan:
# 1. Foreign Key Cascading (ondelete="CASCADE"): Jika akun user atau penerbangan dihapus,
#    seluruh record favorit terkait otomatis terhapus untuk menjaga integritas referensial.
# 2. Unique Constraint (user_id, flight_id): Mencegah duplikasi data favorit yang sama
#    oleh pengguna yang sama (idempoten).

import uuid
from datetime import datetime

from app.models.base import Base, UUIDPrimaryKeyMixin, get_utc_now
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Favorite(Base, UUIDPrimaryKeyMixin):
    """
    Tabel 'favorites' menghubungkan pengguna (user) dengan penerbangan (flight) yang disimpan.
    """

    __tablename__ = "favorites"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Foreign key ke tabel users",
    )
    flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flights.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Foreign key ke tabel flights",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        nullable=False,
        comment="Waktu penerbangan ditambahkan ke favorit (UTC)",
    )

    # Relationships
    flight = relationship("Flight", lazy="joined")

    __table_args__ = (
        UniqueConstraint("user_id", "flight_id", name="uq_user_flight_favorite"),
    )
