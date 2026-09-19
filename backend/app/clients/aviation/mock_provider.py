# ==============================================================================
# Aviation Monitoring & Analytics Platform — Mock Flight Provider
# ==============================================================================
# Implementasi MockFlightProvider berbasis dataset fixture deterministik.
#
# Alasan Arsitektur & Manfaat:
# 1. Zero Quota Consumption: Memungkinkan pengembangan frontend, backend, dan CI pipeline
#    berjalan 100% tanpa menggunakan kuota bulanan Aviationstack yang terbatas.
# 2. Pengujian Deterministik: Menghasilkan data yang konsisten untuk automated test
#    sehingga hasil pengujian stabil dan tidak fluktuatif akibat perubahan data live.
# 3. Representasi Nyata: Fixture mencakup variasi status (active, scheduled, landed, cancelled),
#    rute domestik/internasional, dan kelengkapan data opsional (sebagian punya telemetri, sebagian tidak).

from datetime import UTC, datetime, timedelta

from app.clients.aviation.base import (
    FlightDataProvider,
    FlightDTO,
    FlightSearchQuery,
    FlightSearchResultDTO,
)


def _generate_mock_dataset() -> list[FlightDTO]:
    """Menghasilkan kumpulan data penerbangan contoh yang realistis."""
    now = datetime.now(UTC)
    today_str = now.strftime("%Y-%m-%d")

    return [
        FlightDTO(
            flight_number="DL415",
            flight_date=today_str,
            flight_status="active",
            airline_name="Delta Air Lines",
            airline_iata="DL",
            airline_icao="DAL",
            departure_airport="San Francisco International",
            departure_iata="SFO",
            departure_icao="KSFO",
            departure_scheduled=now - timedelta(hours=2),
            departure_actual=now - timedelta(hours=1, minutes=50),
            departure_terminal="2",
            departure_gate="D11",
            arrival_airport="John F Kennedy International",
            arrival_iata="JFK",
            arrival_icao="KJFK",
            arrival_scheduled=now + timedelta(hours=3),
            arrival_actual=None,
            arrival_terminal="4",
            arrival_gate="B22",
            arrival_baggage="5",
            live_latitude=38.8951,
            live_longitude=-104.8560,
            live_altitude=10363.2,
            live_speed=850.0,
            last_observed_at=now,
        ),
        FlightDTO(
            flight_number="GA404",
            flight_date=today_str,
            flight_status="active",
            airline_name="Garuda Indonesia",
            airline_iata="GA",
            airline_icao="GIA",
            departure_airport="Soekarno-Hatta International",
            departure_iata="CGK",
            departure_icao="WIII",
            departure_scheduled=now - timedelta(minutes=45),
            departure_actual=now - timedelta(minutes=40),
            departure_terminal="3",
            departure_gate="14",
            arrival_airport="Ngurah Rai International",
            arrival_iata="DPS",
            arrival_icao="WADD",
            arrival_scheduled=now + timedelta(minutes=55),
            arrival_actual=None,
            arrival_terminal="D",
            arrival_gate="5",
            arrival_baggage="2",
            live_latitude=-7.5360,
            live_longitude=110.5900,
            live_altitude=9450.0,
            live_speed=780.0,
            last_observed_at=now,
        ),
        FlightDTO(
            flight_number="BA117",
            flight_date=today_str,
            flight_status="scheduled",
            airline_name="British Airways",
            airline_iata="BA",
            airline_icao="BAW",
            departure_airport="London Heathrow",
            departure_iata="LHR",
            departure_icao="EGLL",
            departure_scheduled=now + timedelta(hours=4),
            departure_actual=None,
            departure_terminal="5",
            departure_gate="A10",
            arrival_airport="John F Kennedy International",
            arrival_iata="JFK",
            arrival_icao="KJFK",
            arrival_scheduled=now + timedelta(hours=11),
            arrival_actual=None,
            arrival_terminal="8",
            arrival_gate="12",
            arrival_baggage=None,
            live_latitude=None,
            live_longitude=None,
            live_altitude=None,
            live_speed=None,
            last_observed_at=now,
        ),
        FlightDTO(
            flight_number="JL001",
            flight_date=today_str,
            flight_status="landed",
            airline_name="Japan Airlines",
            airline_iata="JL",
            airline_icao="JAL",
            departure_airport="Tokyo Haneda",
            departure_iata="HND",
            departure_icao="RJTT",
            departure_scheduled=now - timedelta(hours=11),
            departure_actual=now - timedelta(hours=10, minutes=50),
            departure_terminal="3",
            departure_gate="112",
            arrival_airport="San Francisco International",
            arrival_iata="SFO",
            arrival_icao="KSFO",
            arrival_scheduled=now - timedelta(hours=1),
            arrival_actual=now - timedelta(hours=1, minutes=10),
            arrival_terminal="I",
            arrival_gate="A8",
            arrival_baggage="B7",
            live_latitude=37.6190,
            live_longitude=-122.3750,
            live_altitude=0.0,
            live_speed=0.0,
            last_observed_at=now - timedelta(hours=1),
        ),
        FlightDTO(
            flight_number="SQ950",
            flight_date=today_str,
            flight_status="active",
            airline_name="Singapore Airlines",
            airline_iata="SQ",
            airline_icao="SIA",
            departure_airport="Singapore Changi",
            departure_iata="SIN",
            departure_icao="WSSS",
            departure_scheduled=now - timedelta(minutes=30),
            departure_actual=now - timedelta(minutes=25),
            departure_terminal="3",
            departure_gate="B4",
            arrival_airport="Soekarno-Hatta International",
            arrival_iata="CGK",
            arrival_icao="WIII",
            arrival_scheduled=now + timedelta(minutes=50),
            arrival_actual=None,
            arrival_terminal="3",
            arrival_gate="8",
            arrival_baggage=None,
            live_latitude=-1.1200,
            live_longitude=104.8000,
            live_altitude=8200.0,
            live_speed=720.0,
            last_observed_at=now,
        ),
        FlightDTO(
            flight_number="EK358",
            flight_date=today_str,
            flight_status="scheduled",
            airline_name="Emirates",
            airline_iata="EK",
            airline_icao="UAE",
            departure_airport="Dubai International",
            departure_iata="DXB",
            departure_icao="OMDB",
            departure_scheduled=now + timedelta(hours=5),
            departure_actual=None,
            departure_terminal="3",
            departure_gate="C15",
            arrival_airport="Soekarno-Hatta International",
            arrival_iata="CGK",
            arrival_icao="WIII",
            arrival_scheduled=now + timedelta(hours=14),
            arrival_actual=None,
            arrival_terminal="3",
            arrival_gate=None,
            arrival_baggage=None,
            live_latitude=None,
            live_longitude=None,
            live_altitude=None,
            live_speed=None,
            last_observed_at=now,
        ),
        FlightDTO(
            flight_number="QF001",
            flight_date=today_str,
            flight_status="cancelled",
            airline_name="Qantas",
            airline_iata="QF",
            airline_icao="QFA",
            departure_airport="Sydney Kingsford Smith",
            departure_iata="SYD",
            departure_icao="YSSY",
            departure_scheduled=now + timedelta(hours=2),
            departure_actual=None,
            departure_terminal="1",
            departure_gate="9",
            arrival_airport="London Heathrow",
            arrival_iata="LHR",
            arrival_icao="EGLL",
            arrival_scheduled=now + timedelta(hours=24),
            arrival_actual=None,
            arrival_terminal="3",
            arrival_gate=None,
            arrival_baggage=None,
            live_latitude=None,
            live_longitude=None,
            live_altitude=None,
            live_speed=None,
            last_observed_at=now,
        ),
    ]


class MockFlightProvider(FlightDataProvider):
    """
    Provider tiruan (mock) yang menyajikan data dari memori fixture lokal.
    Mendukung penyaringan dinamis dan paginasi yang realistis.
    """

    def __init__(self):
        self._flights = _generate_mock_dataset()

    async def search_flights(self, query: FlightSearchQuery) -> FlightSearchResultDTO:
        filtered = self._flights

        # Filter berdasarkan nomor penerbangan IATA (case-insensitive substring)
        if query.flight_iata:
            query_num = query.flight_iata.strip().upper()
            filtered = [f for f in filtered if query_num in f.flight_number.upper()]

        # Filter berdasarkan nama maskapai
        if query.airline_name:
            query_airline = query.airline_name.strip().lower()
            filtered = [
                f for f in filtered if f.airline_name and query_airline in f.airline_name.lower()
            ]

        # Filter asal bandara (IATA code)
        if query.dep_iata:
            dep_code = query.dep_iata.strip().upper()
            filtered = [f for f in filtered if f.departure_iata == dep_code]

        # Filter tujuan bandara (IATA code)
        if query.arr_iata:
            arr_code = query.arr_iata.strip().upper()
            filtered = [f for f in filtered if f.arrival_iata == arr_code]

        # Filter status penerbangan
        if query.flight_status:
            status_clean = query.flight_status.strip().lower()
            filtered = [f for f in filtered if f.flight_status == status_clean]

        # Filter tanggal penerbangan
        if query.flight_date:
            date_clean = query.flight_date.strip()
            filtered = [f for f in filtered if f.flight_date == date_clean]

        total = len(filtered)
        start_idx = (query.page - 1) * query.limit
        end_idx = start_idx + query.limit
        paged_items = filtered[start_idx:end_idx]

        return FlightSearchResultDTO(
            items=paged_items,
            page=query.page,
            limit=query.limit,
            total=total,
        )

    async def get_flight_by_identifier(
        self, flight_iata: str, flight_date: str | None = None
    ) -> FlightDTO | None:
        target_number = flight_iata.strip().upper()
        for f in self._flights:
            if f.flight_number == target_number:
                if flight_date and f.flight_date != flight_date.strip():
                    continue
                return f
        return None
