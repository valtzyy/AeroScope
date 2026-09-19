# ==============================================================================
# Aviation Monitoring & Analytics Platform — Live Aviationstack Client
# ==============================================================================
# Implementasi client asynchronous untuk upstream API Aviationstack.
#
# Alasan Arsitektur & Keamanan:
# 1. Bounded Exponential Backoff: Hanya melakukan retry maksimal 2 kali pada kegagalan
#    transient (network timeout / 5xx) dengan jeda bertingkat + jitter acak.
# 2. Tidak Me-retry Status 429 & 4xx: Jika kuota habis (429) atau API key salah (401/403),
#    request langsung digagalkan tanpa retry untuk mencegah pemborosan kuota dan pemblokiran IP.
# 3. Isolasi API Key: API key hanya diinjeksi pada query parameter saat HTTP request dikirim,
#    dan tidak pernah disertakan pada pesan exception atau output log.

import asyncio
import random
import time

import httpx
from app.clients.aviation.base import (
    FlightDataProvider,
    FlightDTO,
    FlightSearchQuery,
    FlightSearchResultDTO,
)
from app.clients.aviation.exceptions import (
    ProviderAuthenticationError,
    ProviderCommunicationError,
    ProviderMalformedResponseError,
    ProviderQuotaExceededError,
)
from app.clients.aviation.mapper import map_raw_item_to_flight_dto
from app.clients.aviation.schemas import RawAviationstackResponse
from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.core.metrics import metrics
from pydantic import ValidationError

logger = get_logger(__name__)


class AviationstackProvider(FlightDataProvider):
    """
    Penyedia data penerbangan live yang berkomunikasi langsung dengan Aviationstack API.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ):
        self.api_key = api_key or settings.AVIATIONSTACK_API_KEY
        self.base_url = (base_url or settings.AVIATIONSTACK_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.AVIATIONSTACK_TIMEOUT_SECONDS

        if not self.api_key:
            raise ValueError(
                "AviationstackProvider memerlukan API Key yang valid. "
                "Periksa konfigurasi AVIATIONSTACK_API_KEY Anda."
            )

    async def _send_request_with_retry(self, endpoint: str, params: dict) -> dict:
        """
        Mengirimkan HTTP GET request ke Aviationstack dengan bounded exponential backoff.
        """
        # Injeksi access_key ke query parameters
        request_params = {**params, "access_key": self.api_key}
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        max_retries = 2
        base_delay = 0.5  # 500 ms

        for attempt in range(max_retries + 1):
            start_time = time.perf_counter()
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=request_params)

                latency = time.perf_counter() - start_time
                status_code = response.status_code

                # 1. Catat metrik operasional pemanggilan
                metrics.record_provider_call(latency_seconds=latency, status_code=status_code)

                # 2. Penanganan Status HTTP Spesifik
                if status_code == 200:
                    payload = response.json()
                    # Aviationstack dapat mengembalikan error di dalam body HTTP 200: {"error": {"code": ...}}
                    if isinstance(payload, dict) and "error" in payload:
                        err_info = payload["error"]
                        err_code = str(err_info.get("code", ""))
                        err_msg = str(err_info.get("message", "Upstream API error"))
                        logger.warning("Aviationstack mengembalikan error internal: [%s] %s", err_code, err_msg)

                        if err_code in ("usage_limit_reached", "rate_limit_reached"):
                            raise ProviderQuotaExceededError("Kuota bulanan Aviationstack telah habis.")
                        if err_code in ("invalid_access_key", "missing_access_key"):
                            raise ProviderAuthenticationError("Kunci API Aviationstack tidak valid.")
                        raise ExternalServiceError(f"Aviationstack error: {err_msg}")

                    return payload

                if status_code in (401, 403):
                    # Kunci tidak valid atau akses ditolak: Jangan di-retry
                    raise ProviderAuthenticationError("Otentikasi API key Aviationstack gagal.")

                if status_code == 429:
                    # Batas kuota tercapai: Jangan di-retry agar tidak memperparah throttling
                    raise ProviderQuotaExceededError("Batas kuota request Aviationstack terlampaui.")

                if status_code >= 500:
                    # Upstream server error: Kandidat retry jika masih dalam batas attempt
                    if attempt < max_retries:
                        jitter = random.uniform(0.1, 0.3)
                        delay = (base_delay * (2**attempt)) + jitter
                        logger.warning(
                            "Aviationstack 5xx error (%d), mencoba ulang ke-%d dalam %.2f detik...",
                            status_code,
                            attempt + 1,
                            delay,
                        )
                        await asyncio.sleep(delay)
                        continue
                    raise ExternalServiceError(f"Aviationstack server error HTTP {status_code}")

                # Status 400/422 atau lainnya
                raise ExternalServiceError(f"Aviationstack error respons HTTP {status_code}")

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                latency = time.perf_counter() - start_time
                metrics.record_provider_call(latency_seconds=latency, is_error=True)

                if attempt < max_retries:
                    jitter = random.uniform(0.1, 0.3)
                    delay = (base_delay * (2**attempt)) + jitter
                    logger.warning(
                        "Koneksi timeout/jaringan ke Aviationstack, mencoba ulang ke-%d dalam %.2f detik... (Error: %s)",
                        attempt + 1,
                        delay,
                        str(exc),
                    )
                    await asyncio.sleep(delay)
                    continue
                raise ProviderCommunicationError("Gagal terhubung ke Aviationstack (Network Timeout).") from exc

        raise ExternalServiceError("Gagal menghubungi Aviationstack setelah batas percobaan ulang.")

    async def search_flights(self, query: FlightSearchQuery) -> FlightSearchResultDTO:
        params: dict = {
            "limit": min(query.limit, 100),  # Maksimal 100 item per request
            "offset": (query.page - 1) * query.limit,
        }

        if query.flight_iata:
            params["flight_iata"] = query.flight_iata.strip().upper()
        if query.dep_iata:
            params["dep_iata"] = query.dep_iata.strip().upper()
        if query.arr_iata:
            params["arr_iata"] = query.arr_iata.strip().upper()
        if query.flight_status:
            params["flight_status"] = query.flight_status.strip().lower()
        if query.flight_date:
            params["flight_date"] = query.flight_date.strip()

        payload = await self._send_request_with_retry("flights", params)

        try:
            validated_response = RawAviationstackResponse.model_validate(payload)
        except ValidationError as exc:
            logger.error("Gagal memvalidasi struktur respons Aviationstack: %s", str(exc))
            raise ProviderMalformedResponseError("Format JSON dari Aviationstack tidak valid.") from exc

        items: list[FlightDTO] = [
            map_raw_item_to_flight_dto(item) for item in validated_response.data
        ]

        return FlightSearchResultDTO(
            items=items,
            page=query.page,
            limit=query.limit,
            total=validated_response.pagination.total,
        )

    async def get_flight_by_identifier(
        self, flight_iata: str, flight_date: str | None = None
    ) -> FlightDTO | None:
        query = FlightSearchQuery(
            flight_iata=flight_iata,
            flight_date=flight_date,
            limit=1,
        )
        result = await self.search_flights(query)
        if result.items:
            return result.items[0]
        return None
