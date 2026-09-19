# ==============================================================================
# Aviation Monitoring & Analytics Platform — Flight Observation ORM Model
# ==============================================================================
# Model database relasional untuk snapshot riwayat telemetri penerbangan.
#
# Alasan Arsitektur & Monitoring:
# 1. Pemisahan 'flights' vs 'flight_observations':
#    - Tabel 'flights' menyimpan kondisi TERAKHIR (latest current state) dari penerbangan.
#    - Tabel 'flight_observations' menyimpan deret waktu (time-series) snapshot telemetri
#      (koordinat, ketinggian, kecepatan, status) setiap kali penerbangan diobservasi.
# 2. Indeks Komposit (flight_id, observed_at DESC):
#    Mengoptimasi query riwayat pergerakan pesawat untuk grafik tren ketinggian/kecepatan
#    sehingga database tidak perlu melakukan full table scan.

import uuid
from datetime import datetime

from app.models.base import Base, UUIDPrimaryKeyMixin, get_utc_now
from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class FlightObservation(Base, UUIDPrimaryKeyMixin):
    """
    Tabel 'flight_observations' mencatat titik observasi telemetri historis dari suatu penerbangan.
    """

    __tablename__ = "flight_observations"

    flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flights.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Foreign key ke penerbangan induk di tabel flights",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Status penerbangan saat titik waktu observasi ini",
    )
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    altitude: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Ketinggian dalam meter")
    speed: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Kecepatan dalam km/jam")
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        nullable=False,
        comment="Waktu titik observasi dicatat oleh provider (UTC)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        nullable=False,
        comment="Waktu rekaman masuk ke database lokal (UTC)",
    )

    __table_args__ = (
        # Indeks komposit untuk kueri time-series cepat per penerbangan
        Index("ix_flight_observations_flight_time", "flight_id", observed_at.desc()),
    )
