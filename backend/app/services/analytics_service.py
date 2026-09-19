# ==============================================================================
# Aviation Monitoring & Analytics Platform — Analytics Service Layer
# ==============================================================================
# Service layer yang mengomputasi metrik agregat analitik dari database relasional.
#
# Rumus & Metrik yang Terukur:
# 1. Observed On-Time Rate:
#    (Penerbangan landed dengan keterlambatan <= 15 menit) / (Total penerbangan landed) * 100
# 2. Tracked Flights by Airline:
#    (Jumlah penerbangan maskapai X di DB) / (Total penerbangan di DB) * 100
# 3. Caching Hasil Agregasi:
#    Hasil analitik disimpan di cache selama 60 detik untuk mencegah beban kueri berat
#    GROUP BY / COUNT berulang-ulang pada database saat dashboard dibuka banyak user.

from app.models.flight import Flight
from app.schemas.analytics import (
    AirlineShare,
    AirportTraffic,
    AnalyticsOverviewResponse,
    ObservedDelayMetrics,
    StatusDistribution,
)
from app.services.cache_service import cache_service
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class AnalyticsService:
    """Menghitung data statistik agregat dari basis data penerbangan."""

    @staticmethod
    async def get_overview(session: AsyncSession) -> AnalyticsOverviewResponse:
        """
        Menghasilkan ringkasan analitik komprehensif dari seluruh data yang telah dilacak.
        """
        cache_key = "analytics:overview:latest"
        cached = await cache_service.get(cache_key)
        if cached:
            return AnalyticsOverviewResponse.model_validate(cached)

        # 1. Total penerbangan terlacak
        total_stmt = select(func.count(Flight.id))
        total_flights = (await session.execute(total_stmt)).scalar() or 0

        # 2. Distribusi Status Penerbangan
        status_stmt = select(Flight.flight_status, func.count(Flight.id)).group_by(Flight.flight_status)
        status_rows = (await session.execute(status_stmt)).all()
        status_counts = dict(status_rows)

        distribution = StatusDistribution(
            scheduled=status_counts.get("scheduled", 0),
            active=status_counts.get("active", 0),
            landed=status_counts.get("landed", 0),
            cancelled=status_counts.get("cancelled", 0),
            incident=status_counts.get("incident", 0),
            diverted=status_counts.get("diverted", 0),
        )

        # 3. Perhitungan Observed On-Time Rate
        # Diukur dari penerbangan bertatus 'landed'
        landed_count = distribution.landed
        on_time_rate = None
        delayed_count = 0
        delay_rate = 0.0

        if total_flights > 0:
            # Mengambil sample selisih kedatangan actual vs scheduled
            landed_stmt = select(Flight).where(Flight.flight_status == "landed")
            landed_flights = (await session.execute(landed_stmt)).scalars().all()

            on_time_landed = 0
            for f in landed_flights:
                if f.arrival_scheduled and f.arrival_actual:
                    diff_minutes = (f.arrival_actual - f.arrival_scheduled).total_seconds() / 60
                    if diff_minutes <= 15:
                        on_time_landed += 1
                    else:
                        delayed_count += 1
                else:
                    # Asumsi on-time jika tidak ada pencatatan delay eksplisit
                    on_time_landed += 1

            if landed_count > 0:
                on_time_rate = round((on_time_landed / landed_count) * 100, 1)
            delay_rate = round((delayed_count / total_flights) * 100, 1)

        delay_metrics = ObservedDelayMetrics(
            total_evaluated_flights=landed_count,
            observed_on_time_rate_percent=on_time_rate,
            observed_delayed_flights=delayed_count,
            observed_delay_rate_percent=delay_rate,
        )

        # 4. Sebaran Maskapai (Tracked Flights by Airline)
        airline_stmt = (
            select(Flight.airline_name, Flight.airline_iata, func.count(Flight.id))
            .where(Flight.airline_name.is_not(None))
            .group_by(Flight.airline_name, Flight.airline_iata)
            .order_by(func.count(Flight.id).desc())
            .limit(5)
        )
        airline_rows = (await session.execute(airline_stmt)).all()
        top_airlines: list[AirlineShare] = []
        for name, iata, count in airline_rows:
            pct = round((count / total_flights) * 100, 1) if total_flights > 0 else 0.0
            top_airlines.append(
                AirlineShare(
                    airline_name=name or "Tidak Diketahui",
                    airline_iata=iata,
                    flight_count=count,
                    percentage_of_tracked=pct,
                )
            )

        # 5. Sebaran Bandara Populer (Tracked Flights by Airport)
        dep_airports = (
            await session.execute(
                select(Flight.departure_iata, func.count(Flight.id))
                .where(Flight.departure_iata.is_not(None))
                .group_by(Flight.departure_iata)
            )
        ).all()
        arr_airports = (
            await session.execute(
                select(Flight.arrival_iata, func.count(Flight.id))
                .where(Flight.arrival_iata.is_not(None))
                .group_by(Flight.arrival_iata)
            )
        ).all()

        dep_map = dict(dep_airports)
        arr_map = dict(arr_airports)
        all_codes = set(dep_map.keys()) | set(arr_map.keys())

        airport_list: list[AirportTraffic] = []
        for code in all_codes:
            if not code:
                continue
            deps = dep_map.get(code, 0)
            arrs = arr_map.get(code, 0)
            airport_list.append(
                AirportTraffic(
                    airport_iata=code,
                    departures_count=deps,
                    arrivals_count=arrs,
                )
            )

        # Urutkan berdasarkan total volume lalu lintas
        airport_list.sort(key=lambda a: a.departures_count + a.arrivals_count, reverse=True)
        top_airports = airport_list[:5]

        overview = AnalyticsOverviewResponse(
            total_tracked_flights=total_flights,
            status_distribution=distribution,
            delays=delay_metrics,
            top_airlines=top_airlines,
            top_airports=top_airports,
        )

        # Simpan hasil analitik ke cache selama 60 detik
        await cache_service.set(cache_key, overview.model_dump(mode="json"), ttl_seconds=60)
        return overview


# Singleton instance
analytics_service = AnalyticsService()
