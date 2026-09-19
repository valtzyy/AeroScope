# ==============================================================================
# Aviation Monitoring & Analytics Platform — Backend Dockerfile
# ==============================================================================
# Alasan Desain Dockerfile:
# 1. Base Image 'python:3.13-slim': Menghasilkan image container berukuran kecil (~150MB),
#    mempercepat waktu build CI/CD dan meminimalisir attack surface keamanan.
# 2. Non-root user 'appuser': Menghindari menjalankan aplikasi sebagai root di dalam container,
#    sehingga jika terjadi celah keamanan Remote Code Execution (RCE), penyerang tidak memiliki
#    hak akses sistem operasi host.
# 3. PYTHONDONTWRITEBYTECODE=1: Mencegah Python membuat file .pyc di container yang tidak diperlukan.
# 4. PYTHONUNBUFFERED=1: Memastikan output log aplikasi langsung terkirim ke stdout/stderr secara realtime.

FROM python:3.13-slim AS runner

# Setup variabel lingkungan sistem
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install dependensi sistem minimal untuk kompilasi C (jika diperlukan oleh argon2-cffi/psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependensi Python menggunakan caching layer Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Buat pengguna non-root demi prinsip least privilege
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash -m appuser

# Salin source code aplikasi
COPY . /app

# Berikan izin direktori ke non-root user
RUN chown -R appuser:appgroup /app

# Jalankan sebagai non-root user
USER appuser

EXPOSE 8000

# Healthcheck internal
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Entrypoint menjalankan Uvicorn ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
