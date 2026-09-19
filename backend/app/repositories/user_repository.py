# ==============================================================================
# Aviation Monitoring & Analytics Platform — User Repository
# ==============================================================================
# Layer repositori untuk operasi basis data pengguna (users).
#
# Prinsip Keamanan:
# Menggunakan SQLAlchemy parameterized queries untuk mencegah SQL Injection,
# dan memastikan email selalu dinormalisasi menjadi huruf kecil (lowercase).

import uuid
from datetime import UTC, datetime

from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    """Repositori akses data entitas User."""

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
        """Mengambil profil user berdasarkan primary key UUID."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(session: AsyncSession, email: str) -> User | None:
        """Mencari user berdasarkan email yang telah dinormalisasi."""
        normalized_email = email.strip().lower()
        stmt = select(User).where(User.email == normalized_email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        session: AsyncSession,
        email: str,
        password_hash: str,
        name: str,
        role: str = "USER",
    ) -> User:
        """Membuat dan menyimpan akun user baru ke database."""
        user = User(
            email=email.strip().lower(),
            password_hash=password_hash,
            name=name.strip(),
            role=role.upper(),
        )
        session.add(user)
        await session.flush()
        return user

    @staticmethod
    async def update_last_login(session: AsyncSession, user_id: uuid.UUID) -> None:
        """Memperbarui timestamp login sukses terakhir."""
        user = await UserRepository.get_by_id(session, user_id)
        if user:
            user.last_login_at = datetime.now(UTC)
