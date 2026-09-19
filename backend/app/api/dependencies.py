# ==============================================================================
# Aviation Monitoring & Analytics Platform — API Dependencies
# ==============================================================================
# FastAPI dependency functions untuk otentikasi sesi dan otorisasi peran (RBAC).
#
# Alasan Keamanan:
# 1. Ekstraksi Cookie HttpOnly: Token dibaca dari cookie 'access_token' yang dikirim
#    secara otomatis oleh browser. Fallback header 'Authorization: Bearer' disediakan
#    untuk fleksibilitas pengujian via Postman atau script integration test.
# 2. Re-verifikasi Database: Setelah token JWT diverifikasi secara kriptografis, user
#    tetap diambil dari database untuk memastikan akun belum dihapus atau diblokir.
# 3. RBAC di Backend: Pemeriksaan role 'ADMIN' dilakukan di layer server,
#    menjamin keamanan tidak dapat dimanipulasi dari sisi frontend.

import uuid

from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Mengekstrak dan memverifikasi identitas pengguna aktif dari Cookie atau Authorization Header.
    """
    token: str | None = None

    # 1. Prioritas utama: Baca dari cookie HttpOnly yang aman dari XSS
    if settings.COOKIE_NAME in request.cookies:
        token = request.cookies[settings.COOKIE_NAME]

    # 2. Fallback: Baca dari header Authorization (berguna untuk testing/API client)
    elif "authorization" in request.headers:
        auth_header = request.headers["authorization"]
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()

    if not token:
        raise AuthenticationError("Sesi Anda belum terautentikasi, silakan login terlebih dahulu.")

    # Dekode token JWT dan ekstrak sub (User UUID)
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")

    if not user_id_str:
        raise AuthenticationError("Klaim identitas pengguna pada token tidak valid.")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError as exc:
        raise AuthenticationError("Format ID pengguna dalam token tidak valid.") from exc

    # Ambil data profil terkini dari database
    user = await UserRepository.get_by_id(db, user_uuid)
    if not user:
        raise AuthenticationError("Akun pengguna yang terkait dengan sesi ini tidak ditemukan.")

    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Memastikan pengguna yang login memiliki peran 'ADMIN'.
    Melempar AuthorizationError (HTTP 403) jika hanya memiliki peran 'USER'.
    """
    if current_user.role.upper() != "ADMIN":
        raise AuthorizationError("Akses ditolak: Endpoint ini hanya dapat diakses oleh Administrator.")
    return current_user
