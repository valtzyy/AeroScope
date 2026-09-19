# ==============================================================================
# Aviation Monitoring & Analytics Platform — Search History ORM Model
# ==============================================================================
# Model database relasional untuk riwayat pencarian pengguna terotentikasi.
#
# Alasan Desain:
# 1. Penyimpanan Parameter Fleksibel: Menggunakan kolom JSON (JSONB di PostgreSQL)
#    untuk menyimpan parameter kueri yang bervariasi (rute, maskapai, status, tanggal).
# 2. Indeks Komposit (user_id, searched_at DESC): Mengoptimasi pengambilan riwayat
#    terbaru per pengguna dengan performa kueri O(log N).

import uuid
from datetime import datetime

from app.models.base import Base, UUIDPrimaryKeyMixin, get_utc_now
from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class SearchHistory(Base, UUIDPrimaryKeyMixin):
    """
    Tabel 'search_history' menyimpan riwayat audit pencarian pengguna terdaftar.
    """

    __tablename__ = "search_history"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Foreign key ke tabel users",
    )
    query_parameters: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="Objek JSON berisi parameter pencarian pengguna",
    )
    result_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Jumlah penerbangan yang ditemukan saat pencarian",
    )
    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        nullable=False,
        comment="Waktu pencarian dilakukan (UTC)",
    )

    __table_args__ = (
        Index("ix_search_history_user_time", "user_id", searched_at.desc()),
    )
