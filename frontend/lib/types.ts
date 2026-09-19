// ==============================================================================
// Aviation Monitoring & Analytics Platform — TypeScript Definitions
// ==============================================================================
// Tipe data TypeScript yang mencerminkan kontrak skema API Backend FastAPI.

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}

export interface Flight {
  id: string;
  flight_number: string;
  flight_date: string;
  flight_status: 'scheduled' | 'active' | 'landed' | 'cancelled' | 'incident' | 'diverted';
  airline_name?: string | null;
  airline_iata?: string | null;
  airline_icao?: string | null;
  departure_airport?: string | null;
  departure_iata?: string | null;
  departure_icao?: string | null;
  departure_scheduled?: string | null;
  departure_actual?: string | null;
  departure_terminal?: string | null;
  departure_gate?: string | null;
  arrival_airport?: string | null;
  arrival_iata?: string | null;
  arrival_icao?: string | null;
  arrival_scheduled?: string | null;
  arrival_actual?: string | null;
  arrival_terminal?: string | null;
  arrival_gate?: string | null;
  arrival_baggage?: string | null;
  live_latitude?: number | null;
  live_longitude?: number | null;
  live_altitude?: number | null;
  live_speed?: number | null;
  last_observed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface FlightListResponse {
  data: Flight[];
  meta: PaginationMeta;
  error: null | { code: string; message: string };
}

export interface Observation {
  id: string;
  flight_id: string;
  status: string;
  latitude?: number | null;
  longitude?: number | null;
  altitude?: number | null;
  speed?: number | null;
  observed_at: string;
}

export interface StatusDistribution {
  scheduled: number;
  active: number;
  landed: number;
  cancelled: number;
  incident: number;
  diverted: number;
}

export interface AirlineShare {
  airline_name: string;
  airline_iata?: string | null;
  flight_count: number;
  percentage_of_tracked: number;
}

export interface AirportTraffic {
  airport_iata: string;
  airport_name?: string | null;
  departures_count: number;
  arrivals_count: number;
}

export interface ObservedDelayMetrics {
  total_evaluated_flights: number;
  observed_on_time_rate_percent?: number | null;
  observed_delayed_flights: number;
  observed_delay_rate_percent: number;
}

export interface AnalyticsOverview {
  total_tracked_flights: number;
  status_distribution: StatusDistribution;
  delays: ObservedDelayMetrics;
  top_airlines: AirlineShare[];
  top_airports: AirportTraffic[];
  data_scope_note: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  last_login_at?: string | null;
  created_at: string;
}

export interface Favorite {
  id: string;
  user_id: string;
  flight_id: string;
  created_at: string;
  flight?: Flight | null;
}

export interface SearchHistoryItem {
  id: string;
  user_id: string;
  query_parameters: Record<string, any>;
  result_count: number;
  searched_at: string;
}
