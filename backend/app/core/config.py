# ==============================================================================
# Aviation Monitoring & Analytics Platform — Core Configuration
# ==============================================================================
# Modul ini bertanggung jawab memuat dan memvalidasi konfigurasi aplikasi
# dari environment variables menggunakan Pydantic Settings.
#
# Prinsip Arsitektur:
# 1. Fail-Fast: Jika konfigurasi penting (misal API key atau DB URL) hilang/salah,
#    aplikasi akan langsung berhenti saat booting dengan pesan error yang jelas.
# 2. Type-Safe: Semua variabel memiliki tipe data yang diverifikasi secara otomatis.
# 3. Explicit Provider: Mode 'aviationstack' atau 'mock' ditentukan secara eksplisit,
#    tanpa fallback diam-diam yang dapat membingungkan pengembang.

import json
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Menyimpan seluruh konfigurasi global aplikasi.
    Nilai default disediakan untuk kemudahan pengembangan lokal (development).
    """

    # Identitas & Lingkungan Aplikasi
    APP_NAME: str = "Aviation Monitoring & Analytics Platform"
    APP_ENV: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = False

    # Mode Provider Data Penerbangan
    # 'aviationstack': Mengambil data dari API publik resmi.
    # 'mock': Menggunakan dataset fixture lokal tanpa ketergantungan jaringan.
    FLIGHT_PROVIDER: Literal["aviationstack", "mock"] = "mock"
    ALLOW_MOCK_IN_PRODUCTION: bool = False

    # Konfigurasi Aviationstack API
    # Kunci ini SENSITIF dan hanya dibaca oleh backend.
    AVIATIONSTACK_API_KEY: str = ""
    AVIATIONSTACK_BASE_URL: str = "http://api.aviationstack.com/v1"
    AVIATIONSTACK_TIMEOUT_SECONDS: float = 10.0

    # Database PostgreSQL
    # URL koneksi menggunakan skema asynchronous 'postgresql+asyncpg://'
    DATABASE_URL: str = "postgresql+asyncpg://aviation_user:aviation_password@localhost:5432/aviation_db"

    # Ephemeral Cache & Rate Limiting (Redis)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Keamanan JWT & Otentikasi
    JWT_SECRET: str = "dev_super_secret_jwt_key_at_least_32_characters_long_for_safety"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # Pengaturan Cookie
    # HttpOnly=True mengamankan token dari serangan pembacaan script XSS di browser.
    COOKIE_NAME: str = "access_token"
    COOKIE_SECURE: bool = False  # Setel True di produksi untuk mewajibkan HTTPS
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    # Batasan Rate Limiter (Token Bucket)
    # Melindungi server dan kuota eksternal dari serangan brute-force atau scraping berlebih.
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 5
    RATE_LIMIT_SEARCH_PER_MINUTE: int = 20
    RATE_LIMIT_REFRESH_PER_MINUTE: int = 6

    # CORS (Cross-Origin Resource Sharing)
    # Menentukan domain frontend yang diizinkan memanggil backend dengan kredensial cookie.
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        # Membantu parsing jika format dimasukkan dalam bentuk string JSON di .env
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def validate_provider_and_environment(self) -> "Settings":
        """
        Validasi integritas konfigurasi saat aplikasi dimulai:
        1. Mencegah penggunaan mock provider di production tanpa izin eksplisit.
        2. Memastikan API key Aviationstack tidak kosong jika mode 'aviationstack' dipilih.
        """
        # Larangan penggunaan mock di production secara default
        if (
            self.APP_ENV == "production"
            and self.FLIGHT_PROVIDER == "mock"
            and not self.ALLOW_MOCK_IN_PRODUCTION
        ):
            raise ValueError(
                "Keamanan: FLIGHT_PROVIDER='mock' tidak diizinkan pada APP_ENV='production'. "
                "Gunakan 'aviationstack' atau setel ALLOW_MOCK_IN_PRODUCTION=true jika dalam mode darurat."
            )

        # Pemeriksaan ketersediaan API key pada mode aviationstack
        if self.FLIGHT_PROVIDER == "aviationstack":
            if not self.AVIATIONSTACK_API_KEY or self.AVIATIONSTACK_API_KEY.strip() == "":
                raise ValueError(
                    "Konfigurasi tidak lengkap: AVIATIONSTACK_API_KEY wajib diisi saat "
                    "FLIGHT_PROVIDER disetel ke 'aviationstack'. "
                    "Periksa file .env Anda atau gunakan FLIGHT_PROVIDER='mock' untuk pengujian offline."
                )

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Inisialisasi singleton settings yang akan di-import di seluruh modul aplikasi
settings = Settings()
