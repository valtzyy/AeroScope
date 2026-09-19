# ==============================================================================
# Aviation Monitoring & Analytics Platform — Favorite Repository
# ==============================================================================
# Repositori operasi database untuk entitas Favorite.
#
# Alasan Keamanan:
# Otorisasi Kepemilikan (Ownership Enforcement): Saat pengguna menghapus penerbangan
# favorit, kueri memastikan user_id pada record cocok dengan user_id yang sedang login.
# Ini mencegah serangan Insecure Direct Object References (IDOR).

import uuid

from app.models.favorite import Favorite
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class FavoriteRepository:
    """Mengelola persistensi penerbangan favorit pengguna."""

    @staticmethod
    async def get_user_favorite(
        session: AsyncSession, user_id: uuid.UUID, flight_id: uuid.UUID
    ) -> Favorite | None:
        """Mencari apakah penerbangan tertentu sudah ada di daftar favorit user."""
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.flight_id == flight_id,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def add_favorite(
        session: AsyncSession, user_id: uuid.UUID, flight_id: uuid.UUID
    ) -> Favorite:
        """Menambahkan penerbangan ke daftar favorit secara idempoten."""
        existing = await FavoriteRepository.get_user_favorite(session, user_id, flight_id)
        if existing:
            return existing

        favorite = Favorite(user_id=user_id, flight_id=flight_id)
        session.add(favorite)
        await session.flush()
        return favorite

    @staticmethod
    async def list_user_favorites(
        session: AsyncSession, user_id: uuid.UUID
    ) -> list[Favorite]:
        """Mengambil seluruh daftar penerbangan favorit milik pengguna."""
        stmt = select(Favorite).where(Favorite.user_id == user_id).order_by(Favorite.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def remove_favorite(
        session: AsyncSession, user_id: uuid.UUID, favorite_id: uuid.UUID
    ) -> bool:
        """
        Menghapus entri favorit dengan validasi kepemilikan ketat (user_id).
        Mengembalikan True jika berhasil dihapus, False jika tidak ditemukan atau bukan pemiliknya.
        """
        stmt = select(Favorite).where(
            Favorite.id == favorite_id,
            Favorite.user_id == user_id,  # Validasi kepemilikan mutlak di database
        )
        result = await session.execute(stmt)
        favorite = result.scalar_one_or_none()

        if favorite:
            await session.delete(favorite)
            await session.flush()
            return True
        return False
