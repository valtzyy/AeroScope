# ==============================================================================
# Aviation Monitoring & Analytics Platform — Cryptographic Security
# ==============================================================================
# Modul utilitas keamanan untuk password hashing dan JSON Web Token (JWT).
#
# Alasan Keamanan & Best Practices:
# 1. Mengapa Argon2id?
#    Argon2id adalah pemenang Password Hashing Competition (PHC). Algoritma ini
#    tahan terhadap serangan brute-force berbasis GPU/ASIC karena dirancang membutuhkan
#    alokasi memori (*memory-hard*), bukan sekadar komputasi CPU.
# 2. Token JWT Berumur Pendek (15 Menit):
#    Membatasi jangka waktu penyalahgunaan jika sebuah access token tercuri.
# 3. Kunci Rahasia JWT (JWT_SECRET):
#    Dibaca secara eksklusif dari environment variable dan wajib minimal 32 karakter.

from datetime import UTC, datetime, timedelta

import jwt
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from passlib.context import CryptContext

# Context hashing menggunakan skema Argon2id modern
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Menghasilkan hash password Argon2id dengan salt unik yang dibuat secara otomatis.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Memverifikasi kesesuaian password plaintext terhadap hash yang tersimpan.
    Menggunakan teknik perbandingan konstan (constant-time comparison) untuk mitigasi timing attack.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Membuat JSON Web Token (JWT) yang ditandatangani secara kriptografis menggunakan algoritma HS256.
    Payload menyertakan subject ('sub'), role, timestamp pembuatan ('iat'), dan kedaluwarsa ('exp').
    """
    to_encode = data.copy()
    now = datetime.now(UTC)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
    })

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Memverifikasi keaslian dan masa berlaku JWT.
    Melempar AuthenticationError jika token telah kedaluwarsa atau tandatangan tidak valid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Sesi otentikasi Anda telah berakhir, silakan login kembali.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Token otentikasi tidak valid.") from exc
