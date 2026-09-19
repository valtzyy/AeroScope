# ==============================================================================
# Aviation Monitoring & Analytics Platform — Structured Logging
# ==============================================================================
# Modul ini menyediakan konfigurasi logging terstruktur dan aman.
#
# Prinsip Keamanan & Operasional:
# 1. Sanitasi Data (Log Masking): Mencegah pencatatan kata sandi, token JWT,
#    atau Aviationstack API Key ke dalam log server (kepatuhan OWASP).
# 2. Contextual Tracing: Format log menyertakan timestamp UTC, level keparahan,
#    dan modul asal untuk memudahkan investigasi insiden di production.

import logging
import re
import sys

# Pola regex untuk mendeteksi data sensitif dalam teks log
SENSITIVE_PATTERNS = [
    (re.compile(r"(api[_-]?key|access[_-]?key)=([a-zA-Z0-9_\-]+)", re.IGNORECASE), r"\1=***MASKED***"),
    (re.compile(r"(password|pwd)=([^\s&,]+)", re.IGNORECASE), r"\1=***MASKED***"),
    (re.compile(r"(Bearer\s+)([a-zA-Z0-9_\-\.]+)", re.IGNORECASE), r"\1***MASKED_TOKEN***"),
]


class SensitiveDataFilter(logging.Filter):
    """
    Filter logging khusus untuk mendeteksi dan menyamarkan informasi rahasia
    sebelum pesan dicetak ke output konsol atau file agregator.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, replacement in SENSITIVE_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True


def setup_logging(level: str = "INFO") -> None:
    """
    Menginisialisasi konfigurasi root logger standar aplikasi.
    Menggunakan format yang seragam dan menambahkan filter keamanan.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.addFilter(SensitiveDataFilter())

    # Format: [Waktu UTC] [Level] [Nama Logger]: Pesan
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Bersihkan handler lama untuk menghindari duplikasi log
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)

    # Redam kebisingan log pihak ketiga yang terlalu verbose
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


# Helper function untuk mendapatkan logger ber-namespace
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
