# ==============================================================================
# Aviation Monitoring & Analytics Platform — Authentication Routes
# ==============================================================================
# Endpoint REST API untuk registrasi, login, logout, dan status sesi pengguna.
#
# Alasan Keamanan Cookie HttpOnly:
# 1. Transport Cookie: Token JWT disimpan dalam cookie 'access_token' dengan flag
#    HttpOnly=True, yang membuat kode JavaScript di browser TIDAK DAPAT membaca token.
#    Ini memberikan proteksi tangguh terhadap pencurian token melalui serangan XSS.
# 2. SameSite=Lax: Mencegah browser mengirim cookie pada cross-site request acak (mitigasi CSRF).
# 3. Secure=True di Production: Menjamin cookie hanya ditransmisikan melalui protokol aman HTTPS.

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import auth_service
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Registrasi Pengguna Baru",
)
@limiter.limit(f"{settings.RATE_LIMIT_LOGIN_PER_MINUTE}/minute")
async def register(
    request: Request,
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Mendaftarkan akun baru dengan validasi email unik dan enkripsi password Argon2id.
    """
    user = await auth_service.register(session=db, request=payload)
    return {
        "data": UserResponse.model_validate(user),
        "meta": None,
        "error": None,
    }


@router.post(
    "/login",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Login & Pembuatan Sesi",
)
@limiter.limit(f"{settings.RATE_LIMIT_LOGIN_PER_MINUTE}/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Memverifikasi kredensial pengguna dan menyetel cookie HttpOnly 'access_token'.
    """
    user, token = await auth_service.login(session=db, request=payload)

    # Menyetel cookie HttpOnly yang aman di browser
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return {
        "data": UserResponse.model_validate(user),
        "meta": {"token_type": "bearer", "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60},
        "error": None,
    }


@router.post(
    "/logout",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Logout & Pembersihan Sesi",
)
async def logout(response: Response) -> dict:
    """
    Menghapus cookie otentikasi dari browser untuk mengakhiri sesi aktif.
    """
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        path="/",
        samesite=settings.COOKIE_SAMESITE,
    )
    return {
        "data": {"message": "Anda telah berhasil logout."},
        "meta": None,
        "error": None,
    }


@router.get(
    "/me",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Status Sesi & Profil Pengguna Saat Ini",
)
async def get_me(current_user: User = Depends(get_current_user)) -> dict:
    """
    Mengambil data profil pengguna yang sedang login berdasarkan cookie aktif.
    """
    return {
        "data": UserResponse.model_validate(current_user),
        "meta": None,
        "error": None,
    }
