# ==============================================================================
# Aviation Monitoring & Analytics Platform — Authentication Schemas
# ==============================================================================
# Skema Pydantic v2 untuk validasi pendaftaran, login, dan profil pengguna.
#
# Prinsip Keamanan Input:
# 1. Validasi Kekuatan Password: Minimal 8 karakter.
# 2. Sanitasi Email: Dipangkas (trim) dan dipastikan berformat email standar.

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Permintaan registrasi akun baru."""

    email: EmailStr = Field(description="Alamat email aktif pengguna")
    password: str = Field(min_length=8, max_length=128, description="Kata sandi minimal 8 karakter")
    name: str = Field(min_length=2, max_length=100, description="Nama lengkap pengguna")


class LoginRequest(BaseModel):
    """Permintaan login otentikasi."""

    email: EmailStr = Field(description="Alamat email akun")
    password: str = Field(description="Kata sandi akun")


class UserResponse(BaseModel):
    """Informasi profil publik pengguna yang aman dikembalikan ke client."""

    id: uuid.UUID
    email: str
    name: str
    role: str
    last_login_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
