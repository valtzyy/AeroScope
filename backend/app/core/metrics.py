# ==============================================================================
# Aviation Monitoring & Analytics Platform — Operational Metrics
# ==============================================================================
# Modul ini mencatat metrik penggunaan upstream Aviationstack API secara real-time
# di dalam memori backend.
#
# Alasan Arsitektur & Kesadaran Kuota:
# 1. Aviationstack menerapkan batasan kuota request bulanan (terutama tier free/standard).
# 2. Dengan mencatat metrik request, error, latency, serta rasio cache hit/miss,
#    tim engineering dapat memantau kesehatan integrasi dan mencegah kehabisan kuota tak terduga.

from dataclasses import dataclass, field
from threading import Lock
from typing import Any


@dataclass
class MetricsRegistry:
    """Registry thread-safe untuk menyimpan counter dan durasi operasional provider."""

    _lock: Lock = field(default_factory=Lock)

    # Counter request provider eksternal
    provider_requests_total: int = 0
    provider_errors_total: int = 0
    provider_429_quota_errors: int = 0

    # Latensi pemanggilan eksternal (dalam detik)
    provider_latency_sum_seconds: float = 0.0
    provider_latency_samples: int = 0

    # Efisiensi cache (mengurangi request keluar)
    cache_hits_total: int = 0
    cache_misses_total: int = 0

    def record_provider_call(self, latency_seconds: float, status_code: int | None = None, is_error: bool = False) -> None:
        """Mencatat metrik setelah pemanggilan API Aviationstack."""
        with self._lock:
            self.provider_requests_total += 1
            self.provider_latency_sum_seconds += latency_seconds
            self.provider_latency_samples += 1

            if is_error or (status_code and status_code >= 400):
                self.provider_errors_total += 1

            if status_code == 429:
                self.provider_429_quota_errors += 1

    def record_cache_hit(self) -> None:
        """Mencatat ketika query berhasil disajikan dari Redis tanpa memanggil provider."""
        with self._lock:
            self.cache_hits_total += 1

    def record_cache_miss(self) -> None:
        """Mencatat ketika query tidak ada di cache sehingga harus memanggil provider/DB."""
        with self._lock:
            self.cache_misses_total += 1

    def get_snapshot(self) -> dict[str, Any]:
        """Mengembalikan ringkasan statistik terkini untuk endpoint diagnostik/health."""
        with self._lock:
            total_cache_requests = self.cache_hits_total + self.cache_misses_total
            cache_hit_ratio = (
                round((self.cache_hits_total / total_cache_requests) * 100, 2)
                if total_cache_requests > 0
                else 0.0
            )
            avg_latency_ms = (
                round((self.provider_latency_sum_seconds / self.provider_latency_samples) * 1000, 2)
                if self.provider_latency_samples > 0
                else 0.0
            )

            return {
                "provider_requests_total": self.provider_requests_total,
                "provider_errors_total": self.provider_errors_total,
                "provider_429_quota_errors": self.provider_429_quota_errors,
                "provider_avg_latency_ms": avg_latency_ms,
                "cache_hits_total": self.cache_hits_total,
                "cache_misses_total": self.cache_misses_total,
                "cache_hit_ratio_percent": cache_hit_ratio,
            }


# Inisialisasi singleton registry metrik operasional
metrics = MetricsRegistry()
