# ==============================================================================
# Aviation Monitoring & Analytics Platform — Provider Exceptions
# ==============================================================================
# Taksonomi exception khusus untuk layer integrasi API penerbangan eksternal.
#
# Alasan Desain:
# Memisahkan exception level protokol HTTP (misal httpx.HTTPError) dari
# exception level domain aplikasi, sehingga service layer tidak terikat langsung
# pada pustaka HTTP tertentu.

from app.core.exceptions import ExternalServiceError


class ProviderCommunicationError(ExternalServiceError):
    """Terjadi ketika gagal menjalin koneksi TCP/TLS atau timeout ke Aviationstack."""

    def __init__(self, message: str = "Gagal berkomunikasi dengan provider data penerbangan"):
        super().__init__(message=message, code="PROVIDER_COMMUNICATION_ERROR", status_code=504)


class ProviderAuthenticationError(ExternalServiceError):
    """Terjadi jika API key Aviationstack tidak valid atau tidak diizinkan (HTTP 401/403)."""

    def __init__(self, message: str = "Kunci API provider tidak valid atau tidak memiliki izin"):
        super().__init__(message=message, code="PROVIDER_AUTH_ERROR", status_code=502)


class ProviderQuotaExceededError(ExternalServiceError):
    """Terjadi ketika kuota bulanan atau batas rate limit provider terlampaui (HTTP 429)."""

    def __init__(self, message: str = "Batas kuota request provider data penerbangan telah habis"):
        super().__init__(message=message, code="PROVIDER_QUOTA_EXHAUSTED", status_code=503)


class ProviderMalformedResponseError(ExternalServiceError):
    """Terjadi jika provider mengembalikan struktur JSON yang tidak sesuai dengan kontrak skema."""

    def __init__(self, message: str = "Format data dari provider penerbangan tidak sesuai kontrak"):
        super().__init__(message=message, code="PROVIDER_MALFORMED_DATA", status_code=502)
