# ==============================================================================
# Aviation Monitoring & Analytics Platform — Centralized Domain Exceptions
# ==============================================================================
# Modul ini mendefinisikan taksonomi exception domain aplikasi dan handler
# terpusat untuk FastAPI.
#
# Prinsip Keamanan & Desain API:
# 1. Struktur Respon Terstandarisasi: Semua error dikembalikan dalam bentuk JSON
#    dengan format seragam { "data": null, "meta": null, "error": { "code", "message" } }.
# 2. Tidak Membocorkan Stack Trace: Pesan error yang dikembalikan ke client adalah
#    pesan aman (user-friendly). Rincian teknis internal hanya dicatat di server log.

from typing import Any

from app.core.logging import get_logger
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = get_logger(__name__)


class AppException(Exception):
    """Kelas dasar untuk seluruh domain exception aplikasi."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Any = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class AuthenticationError(AppException):
    """Terjadi ketika kredensial pengguna tidak valid atau token kedaluwarsa."""

    def __init__(self, message: str = "Autentikasi gagal atau sesi telah berakhir", code: str = "AUTHENTICATION_FAILED"):
        super().__init__(message=message, code=code, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(AppException):
    """Terjadi ketika pengguna tidak memiliki izin (hak akses) untuk mengakses resource."""

    def __init__(self, message: str = "Akses ditolak: Anda tidak memiliki izin yang sesuai", code: str = "ACCESS_DENIED"):
        super().__init__(message=message, code=code, status_code=status.HTTP_403_FORBIDDEN)


class ResourceNotFoundError(AppException):
    """Terjadi ketika entitas yang diminta (misal penerbangan atau riwayat) tidak ditemukan."""

    def __init__(self, message: str = "Data yang diminta tidak ditemukan", code: str = "RESOURCE_NOT_FOUND"):
        super().__init__(message=message, code=code, status_code=status.HTTP_404_NOT_FOUND)


class ConflictError(AppException):
    """Terjadi saat pelanggaran constraint data unik (misal email duplikat atau duplicate favorite)."""

    def __init__(self, message: str = "Data yang diajukan mengalami konflik dengan data yang ada", code: str = "RESOURCE_CONFLICT"):
        super().__init__(message=message, code=code, status_code=status.HTTP_409_CONFLICT)


class RateLimitError(AppException):
    """Terjadi ketika frekuensi request client melebihi kuota batas rate limiting."""

    def __init__(self, message: str = "Batas frekuensi permintaan terlampaui, silakan coba lagi beberapa saat", code: str = "RATE_LIMIT_EXCEEDED"):
        super().__init__(message=message, code=code, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


class ExternalServiceError(AppException):
    """Terjadi ketika provider eksternal (Aviationstack) mengalami kegagalan, timeout, atau kuota habis."""

    def __init__(self, message: str = "Layanan data penerbangan eksternal sedang mengalami gangguan", code: str = "EXTERNAL_SERVICE_ERROR", status_code: int = status.HTTP_502_BAD_GATEWAY):
        super().__init__(message=message, code=code, status_code=status_code)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Mendaftarkan global exception handlers ke FastAPI app instance.
    Menjamin tidak ada exception tak terduga yang membocorkan Python stack trace ke client.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "Domain exception tertangkap: [%s] %s | Path: %s",
            exc.code,
            exc.message,
            request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "data": None,
                "meta": None,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Menormalisasi format error validasi Pydantic menjadi format respons standar
        errors = [
            {"field": " -> ".join(str(loc) for loc in err.get("loc", [])), "message": err.get("msg")}
            for err in exc.errors()
        ]
        logger.info("Validasi request gagal pada path: %s | Errors: %s", request.url.path, errors)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "data": None,
                "meta": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Parameter input yang diberikan tidak valid",
                    "details": errors,
                },
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "data": None,
                "meta": None,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "details": None,
                },
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Error internal tidak terduga: Catat stack trace di log, tapi sembunyikan dari user
        logger.error(
            "Unhandled server error: %s | Path: %s",
            str(exc),
            request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "data": None,
                "meta": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Terjadi kesalahan internal pada server kami",
                    "details": None,
                },
            },
        )
