# ==============================================================================
# Unit Tests — Cache Service & Flight Normalization
# ==============================================================================
# Pengujian unit untuk logika normalisasi cache key, perhitungan TTL dinamis,
# dan penyimpanan cache in-memory.

import pytest
from app.clients.aviation.base import FlightSearchQuery
from app.services.cache_service import (
    CacheService,
    build_flight_search_cache_key,
    calculate_ttl_for_status,
)


def test_cache_key_normalization_consistency():
    """Memverifikasi query dengan variasi casing atau spasi menghasilkan cache key identik."""
    q1 = FlightSearchQuery(flight_iata=" dl415 ", dep_iata="sfo", arr_iata="Jfk", flight_status="ACTIVE")
    q2 = FlightSearchQuery(flight_iata="DL415", dep_iata="SFO", arr_iata="jfk", flight_status="active ")

    key1 = build_flight_search_cache_key(q1)
    key2 = build_flight_search_cache_key(q2)

    assert key1 == key2
    assert key1.startswith("flights:search:")


def test_calculate_ttl_for_different_statuses():
    """Memverifikasi durasi TTL yang berbeda berdasarkan kedinamisan status penerbangan."""
    # Active: dinamis (3 menit)
    assert calculate_ttl_for_status("active") == 180
    assert calculate_ttl_for_status("ACTIVE ") == 180

    # Scheduled: sedang (15 menit)
    assert calculate_ttl_for_status("scheduled") == 900

    # Landed/Cancelled: final (2 jam)
    assert calculate_ttl_for_status("landed") == 7200
    assert calculate_ttl_for_status("cancelled") == 7200

    # Default/Unknown
    assert calculate_ttl_for_status(None) == 300
    assert calculate_ttl_for_status("other") == 300


@pytest.mark.asyncio
async def test_cache_service_set_get_and_delete():
    """Memverifikasi operasi dasar set, get, dan delete pada CacheService."""
    cache = CacheService(redis_url="redis://invalid_host_for_fallback:9999/0")

    test_key = "test:flight:123"
    test_data = {"flight_number": "GA404", "status": "active"}

    # Set data
    await cache.set(test_key, test_data, ttl_seconds=60)

    # Get data
    retrieved = await cache.get(test_key)
    assert retrieved == test_data

    # Delete data
    await cache.delete(test_key)
    after_delete = await cache.get(test_key)
    assert after_delete is None
