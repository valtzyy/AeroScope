"""Initial schema: users, flights, flight_observations, favorites, search_history

Revision ID: 20260918_0001
Revises:
Create Date: 2026-09-18 19:25:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260918_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Tabel users
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("role", sa.String(length=20), server_default="USER", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # 2. Tabel flights
    op.create_table(
        "flights",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("flight_number", sa.String(length=20), nullable=False),
        sa.Column("flight_date", sa.String(length=10), nullable=False),
        sa.Column("flight_status", sa.String(length=20), nullable=False),
        sa.Column("external_flight_id", sa.String(length=100), nullable=True),
        sa.Column("airline_name", sa.String(length=100), nullable=True),
        sa.Column("airline_iata", sa.String(length=5), nullable=True),
        sa.Column("airline_icao", sa.String(length=5), nullable=True),
        sa.Column("departure_airport", sa.String(length=150), nullable=True),
        sa.Column("departure_iata", sa.String(length=5), nullable=True),
        sa.Column("departure_icao", sa.String(length=5), nullable=True),
        sa.Column("departure_scheduled", sa.DateTime(timezone=True), nullable=True),
        sa.Column("departure_actual", sa.DateTime(timezone=True), nullable=True),
        sa.Column("departure_terminal", sa.String(length=20), nullable=True),
        sa.Column("departure_gate", sa.String(length=20), nullable=True),
        sa.Column("arrival_airport", sa.String(length=150), nullable=True),
        sa.Column("arrival_iata", sa.String(length=5), nullable=True),
        sa.Column("arrival_icao", sa.String(length=5), nullable=True),
        sa.Column("arrival_scheduled", sa.DateTime(timezone=True), nullable=True),
        sa.Column("arrival_actual", sa.DateTime(timezone=True), nullable=True),
        sa.Column("arrival_terminal", sa.String(length=20), nullable=True),
        sa.Column("arrival_gate", sa.String(length=20), nullable=True),
        sa.Column("arrival_baggage", sa.String(length=20), nullable=True),
        sa.Column("live_latitude", sa.Float(), nullable=True),
        sa.Column("live_longitude", sa.Float(), nullable=True),
        sa.Column("live_altitude", sa.Float(), nullable=True),
        sa.Column("live_speed", sa.Float(), nullable=True),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("flight_number", "flight_date", "departure_iata", "arrival_iata", name="uq_flight_schedule_route"),
    )
    op.create_index(op.f("ix_flights_airline_iata"), "flights", ["airline_iata"], unique=False)
    op.create_index(op.f("ix_flights_arrival_iata"), "flights", ["arrival_iata"], unique=False)
    op.create_index(op.f("ix_flights_departure_iata"), "flights", ["departure_iata"], unique=False)
    op.create_index(op.f("ix_flights_flight_date"), "flights", ["flight_date"], unique=False)
    op.create_index(op.f("ix_flights_flight_number"), "flights", ["flight_number"], unique=False)
    op.create_index(op.f("ix_flights_flight_status"), "flights", ["flight_status"], unique=False)
    op.create_index(op.f("ix_flights_id"), "flights", ["id"], unique=False)
    op.create_index("ix_flights_route", "flights", ["departure_iata", "arrival_iata"], unique=False)

    # 3. Tabel flight_observations
    op.create_table(
        "flight_observations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("flight_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("altitude", sa.Float(), nullable=True),
        sa.Column("speed", sa.Float(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["flight_id"], ["flights.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_flight_observations_flight_id"), "flight_observations", ["flight_id"], unique=False)
    op.create_index(op.f("ix_flight_observations_id"), "flight_observations", ["id"], unique=False)
    op.create_index("ix_flight_observations_flight_time", "flight_observations", ["flight_id", sa.text("observed_at DESC")], unique=False)

    # 4. Tabel favorites
    op.create_table(
        "favorites",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("flight_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["flight_id"], ["flights.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "flight_id", name="uq_user_flight_favorite"),
    )
    op.create_index(op.f("ix_favorites_flight_id"), "favorites", ["flight_id"], unique=False)
    op.create_index(op.f("ix_favorites_id"), "favorites", ["id"], unique=False)
    op.create_index(op.f("ix_favorites_user_id"), "favorites", ["user_id"], unique=False)

    # 5. Tabel search_history
    op.create_table(
        "search_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("query_parameters", sa.JSON(), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False),
        sa.Column("searched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_search_history_id"), "search_history", ["id"], unique=False)
    op.create_index(op.f("ix_search_history_user_id"), "search_history", ["user_id"], unique=False)
    op.create_index("ix_search_history_user_time", "search_history", ["user_id", sa.text("searched_at DESC")], unique=False)


def downgrade() -> None:
    op.drop_table("search_history")
    op.drop_table("favorites")
    op.drop_table("flight_observations")
    op.drop_table("flights")
    op.drop_table("users")
