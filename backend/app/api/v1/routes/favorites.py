# ==============================================================================
# Aviation Monitoring & Analytics Platform — Favorite Flights Endpoints
# ==============================================================================
# Endpoint REST API untuk mengelola penerbangan favorit pengguna.
#
# Alasan Keamanan:
# 1. Seluruh endpoint dilindungi oleh dependency 'get_current_user'.
# 2. Operasi penambahan dan penghapusan selalu mengikat ke identitas user_id aktif,
#    sehingga pengguna tidak dapat mengakses atau memanipulasi favorit milik orang lain.

import uuid

from app.api.dependencies import get_current_user
from app.core.exceptions import ResourceNotFoundError
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.flight_repository import FlightRepository
from app.schemas.favorite import FavoriteCreateRequest, FavoriteResponse
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get(
    "",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Daftar Penerbangan Favorit Pengguna",
)
async def list_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Mengambil semua penerbangan yang telah disimpan ke favorit oleh pengguna yang sedang login.
    """
    favorites = await FavoriteRepository.list_user_favorites(db, current_user.id)
    return {
        "data": [FavoriteResponse.model_validate(fav) for fav in favorites],
        "meta": {"total": len(favorites)},
        "error": None,
    }


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Penerbangan ke Favorit",
)
async def add_favorite(
    request: FavoriteCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Menyimpan penerbangan ke daftar favorit pengguna secara idempoten.
    """
    flight = await FlightRepository.get_by_id(db, request.flight_id)
    if not flight:
        raise ResourceNotFoundError(f"Penerbangan dengan ID {request.flight_id} tidak ditemukan.")

    favorite = await FavoriteRepository.add_favorite(db, current_user.id, request.flight_id)
    return {
        "data": FavoriteResponse.model_validate(favorite),
        "meta": None,
        "error": None,
    }


@router.delete(
    "/{favorite_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Hapus Penerbangan dari Favorit",
)
async def delete_favorite(
    favorite_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Menghapus entri favorit dengan validasi kepemilikan ketat.
    """
    success = await FavoriteRepository.remove_favorite(db, current_user.id, favorite_id)
    if not success:
        raise ResourceNotFoundError(
            f"Favorit dengan ID {favorite_id} tidak ditemukan atau Anda tidak memiliki akses."
        )

    return {
        "data": {"message": "Penerbangan berhasil dihapus dari daftar favorit Anda."},
        "meta": None,
        "error": None,
    }
