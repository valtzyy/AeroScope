# ==============================================================================
# Aviation Monitoring & Analytics Platform — Authentication Service
# ==============================================================================
# Service layer yang mengelola alur bisnis pendaftaran akun dan verifikasi login.
#
# Alasan Keamanan:
# 1. Mitigasi Enumeration Attack: Pada proses login, jika email tidak ditemukan
#    atau password salah, sistem mengembalikan pesan error generik yang sama
#    ("Email atau kata sandi tidak valid"), sehingga penyerang tidak dapat menebak
#    apakah suatu email terdaftar atau tidak.
# 2. Hashing Argon2id: Password plaintext langsung di-hash sebelum disimpan.

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.logging import get_logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class AuthService:
    """Mengelola registrasi pengguna, otentikasi login, dan pembuatan token JWT."""

    @staticmethod
    async def register(session: AsyncSession, request: RegisterRequest) -> User:
        """
        Mendaftarkan pengguna baru setelah memastikan email belum terdaftar.
        """
        existing = await UserRepository.get_by_email(session, request.email)
        if existing:
            raise ConflictError(
                f"Alamat email '{request.email}' sudah terdaftar dalam sistem.",
                code="EMAIL_ALREADY_EXISTS",
            )

        # Hash password menggunakan Argon2id
        hashed_pwd = hash_password(request.password)

        user = await UserRepository.create_user(
            session=session,
            email=request.email,
            password_hash=hashed_pwd,
            name=request.name,
            role="USER",
        )
        logger.info("Pengguna baru berhasil terdaftar: %s (ID: %s)", user.email, user.id)
        return user

    @staticmethod
    async def login(session: AsyncSession, request: LoginRequest) -> tuple[User, str]:
        """
        Memverifikasi kredensial login dan mengembalikan pasangan (User, access_token).
        """
        user = await UserRepository.get_by_email(session, request.email)

        # Menggunakan pesan generik untuk mencegah enumeration attack
        generic_error = AuthenticationError(
            "Email atau kata sandi yang Anda masukkan salah.",
            code="INVALID_CREDENTIALS",
        )

        if not user:
            raise generic_error

        if not verify_password(request.password, user.password_hash):
            raise generic_error

        # Perbarui waktu login terakhir
        await UserRepository.update_last_login(session, user.id)

        # Buat token JWT berumur 15 menit
        token = create_access_token(data={"sub": str(user.id), "role": user.role})
        logger.info("Pengguna berhasil login: %s (ID: %s)", user.email, user.id)

        return user, token


# Singleton instance
auth_service = AuthService()
