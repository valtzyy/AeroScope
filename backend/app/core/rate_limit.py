# ==============================================================================
# Aviation Monitoring & Analytics Platform — Rate Limiting
# ==============================================================================
# Konfigurasi pembatas laju permintaan (Rate Limiter) berbasis Slowapi.
#
# Alasan Keamanan & Perlindungan Kuota:
# 1. Proteksi Brute-Force: Endpoint login dan register dibatasi ketat (misal 5 req/menit)
#    untuk menggagalkan serangan credential stuffing dan pembuatan akun massal.
# 2. Proteksi Kuota Eksternal: Endpoint pencarian dan refresh dibatasi agar satu client
#    tidak menghabiskan seluruh kuota bulanan Aviationstack dalam sekejap.
# 3. Respon Standar: Mengembalikan status HTTP 429 dengan format JSON seragam.

from app.core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

# Inisialisasi limiter berbasis alamat IP client
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    headers_enabled=False,
    storage_uri=settings.REDIS_URL,
)
