# ==============================================================================
# Aviation Monitoring & Analytics Platform — Flight ORM Model
# ==============================================================================
# Model database relasional untuk entitas penerbangan (flights).
#
# Alasan Desain:
# 1. Penyimpanan Data Terpilih: Hanya menyimpan kolom yang bernilai bagi aplikasi
#    (tidak menyalin seluruh JSON mentah dari provider eksternal).
# 2. Indeks Terarah: Menambahkan B-tree index pada flight_number, flight_date,
#    departure_iata, arrival_iata, dan flight_status untuk optimasi performa pencarian.
# 3. Unique Constraint: Menjamin kombinasi nomor penerbangan, tanggal, dan rute unik
#    sehingga proses sinkronisasi (upsert) bersifat idempoten.

from datetime import datetime

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import DateTime, Float, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class Flight(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Tabel 'flights' menyimpan snapshot kondisi terkini dari penerbangan yang telah dilacak.
    """

    __tablename__ = "flights"

    # Nomor penerbangan dan tanggal (misal: DL415, 2026-09-18)
    flight_number: Mapped[str] = mapped_column(
        String(20), index=True, nullable=False, comment="Nomor penerbangan IATA (DL415)"
    )
    flight_date: Mapped[str] = mapped_column(
        String(10), index=True, nullable=False, comment="Tanggal penerbangan format YYYY-MM-DD"
    )
    flight_status: Mapped[str] = mapped_column(
        String(20),
        index=True,
        nullable=False,
        comment="Status penerbangan: scheduled, active, landed, cancelled, incident, diverted",
    )

    # Identitas eksternal opsional dari provider
    external_flight_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="ID unik eksternal dari provider jika tersedia"
    )

    # Maskapai (Airline)
    airline_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    airline_iata: Mapped[str | None] = mapped_column(String(5), index=True, nullable=True)
    airline_icao: Mapped[str | None] = mapped_column(String(5), nullable=True)

    # Keberangkatan (Departure)
    departure_airport: Mapped[str | None] = mapped_column(String(150), nullable=True)
    departure_iata: Mapped[str | None] = mapped_column(String(5), index=True, nullable=True)
    departure_icao: Mapped[str | None] = mapped_column(String(5), nullable=True)
    departure_scheduled: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    departure_actual: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    departure_terminal: Mapped[str | None] = mapped_column(String(20), nullable=True)
    departure_gate: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Kedatangan (Arrival)
    arrival_airport: Mapped[str | None] = mapped_column(String(150), nullable=True)
    arrival_iata: Mapped[str | None] = mapped_column(String(5), index=True, nullable=True)
    arrival_icao: Mapped[str | None] = mapped_column(String(5), nullable=True)
    arrival_scheduled: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    arrival_actual: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    arrival_terminal: Mapped[str | None] = mapped_column(String(20), nullable=True)
    arrival_gate: Mapped[str | None] = mapped_column(String(20), nullable=True)
    arrival_baggage: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Telemetri live terkini (koordinat, ketinggian, kecepatan)
    live_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    live_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    live_altitude: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Ketinggian dalam meter")
    live_speed: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Kecepatan horizontal dalam km/jam")
    last_observed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Waktu observasi telemetri terakhir (UTC)"
    )

    __table_args__ = (
        # Constraint idempoten mencegah pencatatan ganda untuk rute dan hari yang sama
        UniqueConstraint(
            "flight_number",
            "flight_date",
            "departure_iata",
            "arrival_iata",
            name="uq_flight_schedule_route",
        ),
        Index("ix_flights_route", "departure_iata", "arrival_iata"),
    )
