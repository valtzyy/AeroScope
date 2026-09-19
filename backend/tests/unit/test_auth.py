# ==============================================================================
# Unit Tests — Authentication & Cryptography
# ==============================================================================
# Pengujian unit untuk hashing password Argon2id, pembuatan & decoding token JWT,
# dan validasi skema otentikasi.

from datetime import timedelta

import pytest
from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.schemas.auth import RegisterRequest
from pydantic import ValidationError


def test_password_hashing_and_verification():
    """Memverifikasi password di-hash dengan Argon2id dan dapat diverifikasi dengan benar."""
    raw_password = "SecurePassword123!"
    hashed = hash_password(raw_password)

    # Hash tidak boleh sama dengan plaintext
    assert hashed != raw_password
    assert "$argon2" in hashed

    # Verifikasi sukses untuk password yang cocok
    assert verify_password(raw_password, hashed) is True

    # Verifikasi gagal untuk password yang salah
    assert verify_password("WrongPassword999", hashed) is False


def test_jwt_token_creation_and_decoding():
    """Memverifikasi payload JWT dienkode dan didekode dengan akurat."""
    data = {"sub": "123e4567-e89b-12d3-a456-426614174000", "role": "USER"}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=5))

    payload = decode_access_token(token)
    assert payload["sub"] == data["sub"]
    assert payload["role"] == "USER"
    assert "exp" in payload
    assert "iat" in payload


def test_expired_jwt_token_raises_authentication_error():
    """Memverifikasi token yang kedaluwarsa melempar AuthenticationError."""
    # Buat token dengan masa berlaku negatif (sudah kedaluwarsa)
    data = {"sub": "test_user_id"}
    expired_token = create_access_token(data=data, expires_delta=timedelta(minutes=-10))

    with pytest.raises(AuthenticationError) as exc_info:
        decode_access_token(expired_token)
    assert "berakhir" in str(exc_info.value)


def test_register_schema_validation():
    """Memverifikasi validasi skema pendaftaran: email valid dan panjang password minimal 8."""
    # Valid
    valid_req = RegisterRequest(email="pilot@example.com", password="password123", name="Pilot Test")
    assert valid_req.email == "pilot@example.com"

    # Password terlalu pendek (< 8 karakter)
    with pytest.raises(ValidationError):
        RegisterRequest(email="pilot@example.com", password="short", name="Pilot Test")

    # Format email tidak valid
    with pytest.raises(ValidationError):
        RegisterRequest(email="invalid-email-string", password="password123", name="Pilot Test")
