# ==============================================================================
# Aviation Monitoring & Analytics Platform — Cache Service (Cache-Aside)
# ==============================================================================
# Layanan caching ephemeral menggunakan Redis dengan fallback in-memory aman.
#
# Alasan Arsitektur & Pola Cache-Aside:
# 1. Mengurangi Beban Upstream: Setiap request pencarian penerbangan diperiksa di cache
#    terlebih dahulu untuk menghemat kuota Aviationstack.
# 2. Normalisasi Cache Key: Menghindari cache fragmentation (misal 'SFO' vs 'sfo' atau
#    perbedaan urutan parameter) dengan membuat hash SHA-256 dari parameter terurut.
# 3. Dynamic TTL (Time-To-Live):
#    - Penerbangan 'active' diberi TTL 3 menit (telemetri live cepat berubah).
#    - Penerbangan 'scheduled' diberi TTL 15 menit.
#    - Penerbangan 'landed'/'cancelled' diberi TTL 120 menit (status sudah final).
# 4. Ephemeral Redis: Redis tidak menyimpan data permanen ke disk, sehingga aman restart
#    kapan saja dan data akan terisi kembali secara otomatis saat cache miss.

import hashlib
import json
from typing import Any

import redis.asyncio as aioredis
from app.clients.aviation.base import FlightSearchQuery
from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import metrics

logger = get_logger(__name__)


def build_flight_search_cache_key(query: FlightSearchQuery) -> str:
    """
    Menghasilkan cache key unik dan deterministik dari parameter query.
    Semua string di-trim dan di-lowercase agar query yang ekuivalen menghasilkan key yang sama.
    """
    normalized_params = {
        "flight": (query.flight_iata.strip().upper()) if query.flight_iata else "",
        "airline": (query.airline_name.strip().lower()) if query.airline_name else "",
        "dep": (query.dep_iata.strip().upper()) if query.dep_iata else "",
        "arr": (query.arr_iata.strip().upper()) if query.arr_iata else "",
        "status": (query.flight_status.strip().lower()) if query.flight_status else "",
        "date": query.flight_date.strip() if query.flight_date else "",
        "page": query.page,
        "limit": query.limit,
    }
    sorted_str = json.dumps(normalized_params, sort_keys=True)
    digest = hashlib.sha256(sorted_str.encode("utf-8")).hexdigest()[:16]
    return f"flights:search:{digest}"


def calculate_ttl_for_status(status_val: str | None) -> int:
    """Menentukan durasi TTL (detik) berdasarkan tingkat kedinamisan status penerbangan."""
    if not status_val:
        return 300  # Default 5 menit

    clean = status_val.strip().lower()
    if clean == "active":
        return 180  # 3 menit untuk penerbangan sedang terbang
    if clean == "scheduled":
        return 900  # 15 menit untuk penerbangan terjadwal
    if clean in ("landed", "cancelled"):
        return 7200  # 2 jam untuk penerbangan yang sudah selesai

    return 300


class CacheService:
    """Mengelola pembacaan dan penyimpanan cache ephemeral."""

    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._memory_cache: dict[str, Any] = {}
        self._redis_client: aioredis.Redis | None = None

    async def _get_client(self) -> aioredis.Redis | None:
        if self._redis_client is None:
            try:
                self._redis_client = aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_timeout=1.5,
                )
            except Exception as exc:
                logger.warning("Gagal menginisialisasi Redis client: %s (menggunakan fallback in-memory)", exc)
                return None
        return self._redis_client

    async def get(self, key: str) -> Any | None:
        """Mengambil data dari cache (Redis dengan fallback in-memory)."""
        client = await self._get_client()
        if client:
            try:
                val = await client.get(key)
                if val:
                    metrics.record_cache_hit()
                    return json.loads(val)
                metrics.record_cache_miss()
                return None
            except Exception as exc:
                logger.debug("Redis get gagal, fallback ke in-memory: %s", exc)

        # Fallback in-memory
        if key in self._memory_cache:
            metrics.record_cache_hit()
            return self._memory_cache[key]

        metrics.record_cache_miss()
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Menyimpan data ke cache dengan batas waktu kedaluwarsa (TTL)."""
        serialized = json.dumps(value, default=str)
        client = await self._get_client()
        if client:
            try:
                await client.set(key, serialized, ex=ttl_seconds)
                return
            except Exception as exc:
                logger.debug("Redis set gagal, menyimpan di in-memory: %s", exc)

        # Fallback in-memory
        self._memory_cache[key] = value

    async def delete(self, key: str) -> None:
        """Menghapus key spesifik dari cache."""
        client = await self._get_client()
        if client:
            try:
                await client.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)

    async def close(self) -> None:
        if self._redis_client:
            await self._redis_client.aclose()


# Singleton instance CacheService
cache_service = CacheService()
