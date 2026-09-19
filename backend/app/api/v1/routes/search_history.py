# ==============================================================================
# Aviation Monitoring & Analytics Platform — Search History Endpoints
# ==============================================================================
# Endpoint REST API untuk melihat dan menghapus riwayat pencarian pengguna aktif.
#
# Alasan Keamanan:
# Setiap query dan mutasi riwayat secara mutlak terikat ke current_user.id.

import math
import uuid
from typing import Annotated

from app.api.dependencies import get_current_user
from app.core.exceptions import ResourceNotFoundError
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.search_history_repository import SearchHistoryRepository
from app.schemas.flight import PaginationMeta
from app.schemas.search_history import SearchHistoryListResponse, SearchHistoryResponse
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/search-history", tags=["Search History"])


@router.get(
    "",
    response_model=SearchHistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Daftar Riwayat Pencarian Pengguna",
)
async def list_search_history(
    page: Annotated[int, Query(ge=1, description="Nomor halaman riwayat")] = 1,
    limit: Annotated[int, Query(ge=1, le=50, description="Jumlah item per halaman")] = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SearchHistoryListResponse:
    """
    Mengambil riwayat pencarian penerbangan milik pengguna aktif dengan paginasi.
    """
    history_items, total = await SearchHistoryRepository.list_user_history(
        session=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
    )
    total_pages = math.ceil(total / limit) if total > 0 else 0

    return SearchHistoryListResponse(
        data=[SearchHistoryResponse.model_validate(h) for h in history_items],
        meta=PaginationMeta(page=page, limit=limit, total=total, total_pages=total_pages),
    )


@router.delete(
    "/{history_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Hapus Satu Entri Riwayat Pencarian",
)
async def delete_search_history_entry(
    history_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Menghapus satu entri riwayat pencarian dengan validasi kepemilikan.
    """
    success = await SearchHistoryRepository.delete_history_item(
        session=db,
        user_id=current_user.id,
        history_id=history_id,
    )
    if not success:
        raise ResourceNotFoundError(
            f"Riwayat pencarian dengan ID {history_id} tidak ditemukan atau Anda tidak memiliki izin."
        )

    return {
        "data": {"message": "Entri riwayat pencarian berhasil dihapus."},
        "meta": None,
        "error": None,
    }
