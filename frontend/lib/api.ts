// ==============================================================================
// Aviation Monitoring & Analytics Platform — Frontend API Client
// ==============================================================================
// Modul ini membungkus seluruh pemanggilan HTTP REST API ke backend FastAPI kita.
//
// Alasan Arsitektur & Keamanan:
// 1. Tidak Pernah Memanggil Aviationstack Langsung:
//    Seluruh fungsi di sini memanggil endpoint internal (/api/v1/*), BUKAN Aviationstack.
//    Ini menjamin Aviationstack API key tidak pernah bocor ke sisi client.
// 2. credentials: 'include':
//    Wajib disertakan agar browser secara otomatis mengirimkan cookie HttpOnly 'access_token'
//    pada setiap request tanpa perlu membaca token melalui kode JavaScript (proteksi XSS).

import {
  AnalyticsOverview,
  Favorite,
  Flight,
  FlightListResponse,
  Observation,
  SearchHistoryItem,
  User,
} from './types';

const API_BASE = '/api/v1';

async function fetcher<T>(url: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(url, {
    ...options,
    // Memastikan cookie otentikasi selalu disertakan pada request
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  const body = await res.json().catch(() => null);

  if (!res.ok) {
    const errorMsg = body?.error?.message || `HTTP request gagal dengan status ${res.status}`;
    throw new Error(errorMsg);
  }

  return body.data !== undefined ? body.data : body;
}

// ----------------------------------------------------------------------
// Flights
// ----------------------------------------------------------------------
export async function searchFlights(params: {
  flight_number?: string;
  airline?: string;
  dep_iata?: string;
  arr_iata?: string;
  flight_status?: string;
  date?: string;
  page?: number;
  limit?: number;
}): Promise<FlightListResponse> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== '') {
      query.append(key, String(val));
    }
  });

  const res = await fetch(`${API_BASE}/flights?${query.toString()}`, {
    credentials: 'include',
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message || 'Gagal mencari data penerbangan');
  }

  return res.json();
}

export async function getFlightDetail(flightId: string): Promise<Flight> {
  return fetcher<Flight>(`${API_BASE}/flights/${flightId}`);
}

export async function refreshFlight(flightId: string): Promise<Flight> {
  return fetcher<Flight>(`${API_BASE}/flights/${flightId}/refresh`, {
    method: 'POST',
  });
}

export async function getFlightObservations(flightId: string): Promise<Observation[]> {
  return fetcher<Observation[]>(`${API_BASE}/flights/${flightId}/observations`);
}

// ----------------------------------------------------------------------
// Analytics
// ----------------------------------------------------------------------
export async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  return fetcher<AnalyticsOverview>(`${API_BASE}/analytics/overview`);
}

// ----------------------------------------------------------------------
// Authentication
// ----------------------------------------------------------------------
export async function loginUser(email: string, password: string): Promise<User> {
  return fetcher<User>(`${API_BASE}/auth/login`, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function registerUser(email: string, password: string, name: string): Promise<User> {
  return fetcher<User>(`${API_BASE}/auth/register`, {
    method: 'POST',
    body: JSON.stringify({ email, password, name }),
  });
}

export async function logoutUser(): Promise<{ message: string }> {
  return fetcher<{ message: string }>(`${API_BASE}/auth/logout`, {
    method: 'POST',
  });
}

export async function getCurrentUser(): Promise<User> {
  return fetcher<User>(`${API_BASE}/auth/me`);
}

// ----------------------------------------------------------------------
// Favorites
// ----------------------------------------------------------------------
export async function getFavorites(): Promise<Favorite[]> {
  return fetcher<Favorite[]>(`${API_BASE}/favorites`);
}

export async function addFavorite(flightId: string): Promise<Favorite> {
  return fetcher<Favorite>(`${API_BASE}/favorites`, {
    method: 'POST',
    body: JSON.stringify({ flight_id: flightId }),
  });
}

export async function removeFavorite(favoriteId: string): Promise<{ message: string }> {
  return fetcher<{ message: string }>(`${API_BASE}/favorites/${favoriteId}`, {
    method: 'DELETE',
  });
}

// ----------------------------------------------------------------------
// Search History
// ----------------------------------------------------------------------
export async function getSearchHistory(
  page: number = 1,
  limit: number = 20
): Promise<{ data: SearchHistoryItem[]; meta: any }> {
  const res = await fetch(`${API_BASE}/search-history?page=${page}&limit=${limit}`, {
    credentials: 'include',
  });
  if (!res.ok) {
    throw new Error('Gagal mengambil riwayat pencarian');
  }
  return res.json();
}

export async function deleteSearchHistory(historyId: string): Promise<{ message: string }> {
  return fetcher<{ message: string }>(`${API_BASE}/search-history/${historyId}`, {
    method: 'DELETE',
  });
}
