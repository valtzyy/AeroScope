# ==============================================================================
# Aviation Monitoring & Analytics Platform — User ORM Model
# ==============================================================================
# Model database relasional untuk akun pengguna (users) dan otorisasi peran (RBAC).
#
# Alasan Keamanan & Desain:
# 1. Hashing Password: Hanya hash password (Argon2id) yang disimpan di kolom 'password_hash'.
#    Password plaintext dilarang keras masuk ke database.
# 2. Case-Insensitive Email: Email dinormalisasi menjadi huruf kecil dan memiliki index unik.
# 3. RBAC (Role-Based Access Control): Kolom 'role' mendukung nilai 'USER' atau 'ADMIN'
#    yang diperiksa di backend untuk pembatasan hak akses.

from datetime import datetime

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Tabel 'users' menyimpan profil pengguna, kredensial terenkripsi, dan peran otorisasi.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="Alamat email unik pengguna (huruf kecil)",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Hash password Argon2id terenkripsi dengan salt acak",
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nama lengkap tampilan pengguna",
    )
    role: Mapped[str] = mapped_column(
        String(20),
        default="USER",
        nullable=False,
        comment="Peran otorisasi sistem: 'USER' atau 'ADMIN'",
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Waktu pencatatan login sukses terakhir (UTC)",
    )
