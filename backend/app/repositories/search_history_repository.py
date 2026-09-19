# ==============================================================================
# Aviation Monitoring & Analytics Platform — Search History Repository
# ==============================================================================
# Repositori operasi database untuk riwayat pencarian pengguna.
#
# Alasan Keamanan:
# Memvalidasi kepemilikan (user_id) pada setiap operasi pembacaan dan penghapusan
# riwayat pencarian untuk menjamin isolasi data antar pengguna.

import uuid

from app.models.search_history import SearchHistory
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class SearchHistoryRepository:
    """Mengelola pencatatan dan pengambilan riwayat pencarian pengguna."""

    @staticmethod
    async def record_search(
        session: AsyncSession,
        user_id: uuid.UUID,
        query_parameters: dict,
        result_count: int,
    ) -> SearchHistory:
        """Menyimpan entri riwayat pencarian baru."""
        history = SearchHistory(
            user_id=user_id,
            query_parameters=query_parameters,
            result_count=result_count,
        )
        session.add(history)
        await session.flush()
        return history

    @staticmethod
    async def list_user_history(
        session: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[SearchHistory], int]:
        """Mengambil riwayat pencarian berpaginasi milik pengguna aktif."""
        stmt = select(SearchHistory).where(SearchHistory.user_id == user_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await session.execute(count_stmt)).scalar() or 0

        offset_val = (page - 1) * limit
        stmt = stmt.order_by(SearchHistory.searched_at.desc()).offset(offset_val).limit(limit)

        results = await session.execute(stmt)
        return list(results.scalars().all()), total

    @staticmethod
    async def delete_history_item(
        session: AsyncSession, user_id: uuid.UUID, history_id: uuid.UUID
    ) -> bool:
        """Menghapus satu riwayat pencarian dengan validasi kepemilikan ketat."""
        stmt = select(SearchHistory).where(
            SearchHistory.id == history_id,
            SearchHistory.user_id == user_id,
        )
        result = await session.execute(stmt)
        entry = result.scalar_one_or_none()

        if entry:
            await session.delete(entry)
            await session.flush()
            return True
        return False
