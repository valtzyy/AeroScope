'use client';

// ==============================================================================
// Aviation Monitoring & Analytics Platform — Flight Detail Page
// ==============================================================================
// Halaman rincian lengkap penerbangan, telemetri live, dan riwayat observasi historis.
//
// Alasan Desain & Resiliensi:
// 1. Penanganan Nilai Nullable: Field seperti gate, terminal, baggage, dan koordinat
//    ditampilkan sebagai "Not available" jika provider belum memilikinya.
// 2. Progres Rute Estimasi: Alur visual berlabel eksplisit "Estimasi Progres Rute
//    (Interpretasi Aplikasi)" agar tidak memalsukan status resmi provider.

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getFlightDetail, getFlightObservations, refreshFlight, addFavorite } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import {
  ArrowLeft,
  Plane,
  RefreshCw,
  Clock,
  MapPin,
  Compass,
  Gauge,
  Calendar,
  Bookmark,
  CheckCircle2,
  AlertCircle,
  Activity,
} from 'lucide-react';

export default function FlightDetailPage() {
  const params = useParams();
  const flightId = params.id as string;
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [feedback, setFeedback] = useState<string | null>(null);

  // Fetch detail flight
  const {
    data: flight,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['flight-detail', flightId],
    queryFn: () => getFlightDetail(flightId),
    enabled: !!flightId,
  });

  // Fetch telemetry observations
  const { data: observations, isLoading: obsLoading } = useQuery({
    queryKey: ['flight-observations', flightId],
    queryFn: () => getFlightObservations(flightId),
    enabled: !!flightId,
  });

  // Refresh flight mutation
  const refreshMutation = useMutation({
    mutationFn: () => refreshFlight(flightId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flight-detail', flightId] });
      queryClient.invalidateQueries({ queryKey: ['flight-observations', flightId] });
      setFeedback('Data dan telemetri penerbangan berhasil diperbarui!');
      setTimeout(() => setFeedback(null), 3500);
    },
    onError: (err: any) => {
      setFeedback(err?.message || 'Gagal memperbarui data penerbangan');
      setTimeout(() => setFeedback(null), 3500);
    },
  });

  // Add favorite mutation
  const favoriteMutation = useMutation({
    mutationFn: () => addFavorite(flightId),
    onSuccess: () => {
      setFeedback('Penerbangan berhasil disimpan ke daftar favorit!');
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
      setTimeout(() => setFeedback(null), 3000);
    },
    onError: (err: any) => {
      setFeedback(err?.message || 'Gagal menyimpan ke favorit');
      setTimeout(() => setFeedback(null), 3000);
    },
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[450px] space-y-4">
        <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
        <p className="text-sm text-slate-400">Memuat rincian data penerbangan...</p>
      </div>
    );
  }

  if (isError || !flight) {
    return (
      <div className="glass-panel p-8 rounded-2xl text-center max-w-lg mx-auto space-y-4 border-rose-500/30">
        <AlertCircle className="w-12 h-12 text-rose-400 mx-auto" />
        <h2 className="text-lg font-bold text-white">Data Penerbangan Tidak Ditemukan</h2>
        <p className="text-sm text-slate-400">
          {(error as Error)?.message || 'Penerbangan yang Anda cari mungkin tidak ada atau telah dihapus.'}
        </p>
        <Link
          href="/flights"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm text-slate-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Kembali ke Daftar Penerbangan
        </Link>
      </div>
    );
  }

  const formatDateTime = (iso?: string | null) => {
    if (!iso) return 'Not available';
    try {
      const d = new Date(iso);
      return d.toLocaleString('id-ID', {
        dateStyle: 'medium',
        timeStyle: 'short',
      });
    } catch {
      return 'Not available';
    }
  };

  return (
    <div className="space-y-8">
      {/* Back link & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <Link
          href="/flights"
          className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-cyan-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Kembali ke Pencarian
        </Link>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              if (!user) {
                setFeedback('Silakan masuk (login) terlebih dahulu untuk menyimpan ke favorit.');
                setTimeout(() => setFeedback(null), 3500);
                return;
              }
              favoriteMutation.mutate();
            }}
            disabled={favoriteMutation.isPending}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-medium text-amber-400 transition-colors"
          >
            <Bookmark className="w-4 h-4" />
            Simpan Favorit
          </button>
          <button
            onClick={() => refreshMutation.mutate()}
            disabled={refreshMutation.isPending}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md shadow-cyan-600/20 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
            Refresh Status
          </button>
        </div>
      </div>

      {/* Notification Toast */}
      {feedback && (
        <div className="p-3.5 rounded-xl bg-cyan-950/90 border border-cyan-500/40 text-cyan-200 text-sm flex items-center justify-between">
          <span>{feedback}</span>
          <button onClick={() => setFeedback(null)} className="text-cyan-400 hover:text-white text-xs">
            Tutup
          </button>
        </div>
      )}

      {/* Hero Flight Card */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Plane className="w-7 h-7 transform -rotate-45" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-black font-mono text-white tracking-wider">
                  {flight.flight_number}
                </h1>
                <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-slate-800 border border-slate-700 text-cyan-300">
                  {flight.flight_status}
                </span>
              </div>
              <p className="text-sm text-slate-400 mt-0.5">
                {flight.airline_name || 'Maskapai Tidak Dikenal'} ({flight.airline_iata || '—'})
              </p>
            </div>
          </div>

          <div className="text-right">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 justify-end">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              <span>Tanggal Penerbangan: {flight.flight_date}</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              Terakhir Disinkronkan: {formatDateTime(flight.last_observed_at || flight.updated_at)}
            </p>
          </div>
        </div>

        {/* Origin & Destination Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Departure Card */}
          <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5" /> Keberangkatan (Departure)
              </span>
              <span className="text-2xl font-black font-mono text-white">{flight.departure_iata || '—'}</span>
            </div>
            <p className="text-sm font-semibold text-slate-200">{flight.departure_airport || 'Nama Bandara Tidak Tersedia'}</p>
            
            <div className="grid grid-cols-2 gap-3 text-xs pt-2 border-t border-slate-800/80">
              <div>
                <span className="text-slate-400 block">Jadwal Keberangkatan</span>
                <span className="text-slate-200 font-medium font-mono">{formatDateTime(flight.departure_scheduled)}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Realisasi Keberangkatan</span>
                <span className="text-slate-200 font-medium font-mono">{formatDateTime(flight.departure_actual)}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Terminal</span>
                <span className="text-slate-200 font-medium">{flight.departure_terminal || 'Not available'}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Gerbang (Gate)</span>
                <span className="text-slate-200 font-medium">{flight.departure_gate || 'Not available'}</span>
              </div>
            </div>
          </div>

          {/* Arrival Card */}
          <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5" /> Kedatangan (Arrival)
              </span>
              <span className="text-2xl font-black font-mono text-white">{flight.arrival_iata || '—'}</span>
            </div>
            <p className="text-sm font-semibold text-slate-200">{flight.arrival_airport || 'Nama Bandara Tidak Tersedia'}</p>

            <div className="grid grid-cols-2 gap-3 text-xs pt-2 border-t border-slate-800/80">
              <div>
                <span className="text-slate-400 block">Jadwal Kedatangan</span>
                <span className="text-slate-200 font-medium font-mono">{formatDateTime(flight.arrival_scheduled)}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Realisasi Kedatangan</span>
                <span className="text-slate-200 font-medium font-mono">{formatDateTime(flight.arrival_actual)}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Terminal & Gate</span>
                <span className="text-slate-200 font-medium">
                  {flight.arrival_terminal ? `T${flight.arrival_terminal}` : 'Not available'} / {flight.arrival_gate || '—'}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block">Pengambilan Bagasi</span>
                <span className="text-slate-200 font-medium">{flight.arrival_baggage || 'Not available'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Live Telemetry Card */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Activity className="w-5 h-5 text-emerald-400" />
          Status Telemetri Live Terkini
        </h2>
        
        {flight.live_latitude !== null && flight.live_longitude !== null ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400">Ketinggian (Altitude)</span>
              <p className="text-xl font-bold font-mono text-cyan-400">
                {flight.live_altitude ? `${flight.live_altitude.toLocaleString('id-ID')} m` : 'Not available'}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400">Kecepatan (Speed)</span>
              <p className="text-xl font-bold font-mono text-emerald-400">
                {flight.live_speed ? `${flight.live_speed} km/h` : 'Not available'}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400">Garis Lintang (Latitude)</span>
              <p className="text-xl font-bold font-mono text-slate-200">
                {flight.live_latitude !== null && flight.live_latitude !== undefined ? `${flight.live_latitude.toFixed(4)}°` : '—'}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400">Garis Bujur (Longitude)</span>
              <p className="text-xl font-bold font-mono text-slate-200">
                {flight.live_longitude !== null && flight.live_longitude !== undefined ? `${flight.live_longitude.toFixed(4)}°` : '—'}
              </p>
            </div>
          </div>
        ) : (
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 text-center text-slate-400 text-sm">
            <p>Data radar telemetri live tidak tersedia untuk penerbangan ini saat ini.</p>
          </div>
        )}
      </div>

      {/* Observation History Timeline */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Clock className="w-5 h-5 text-cyan-400" />
          Riwayat Rekam Jejak Observasi (Time-Series)
        </h2>
        <p className="text-xs text-slate-400">
          Setiap pembaruan status dan telemetri disimpan sebagai snapshot observasi untuk analisis pergerakan historis.
        </p>

        {obsLoading ? (
          <p className="text-xs text-slate-400 animate-pulse">Memuat riwayat observasi...</p>
        ) : !observations || observations.length === 0 ? (
          <p className="text-xs text-slate-400">Belum ada titik observasi tercatat untuk penerbangan ini.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="py-2.5 px-3">Waktu Observasi (UTC)</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Koordinat (Lat / Lon)</th>
                  <th className="py-2.5 px-3 text-right">Ketinggian</th>
                  <th className="py-2.5 px-3 text-right">Kecepatan</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
                {observations.map((obs) => (
                  <tr key={obs.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 text-slate-400">{formatDateTime(obs.observed_at)}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-bold uppercase text-[10px]">
                        {obs.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      {obs.latitude !== null && obs.longitude !== null
                        ? `${obs.latitude?.toFixed(2)}°, ${obs.longitude?.toFixed(2)}°`
                        : '—'}
                    </td>
                    <td className="py-2.5 px-3 text-right text-cyan-400">
                      {obs.altitude !== null ? `${obs.altitude} m` : '—'}
                    </td>
                    <td className="py-2.5 px-3 text-right text-emerald-400">
                      {obs.speed !== null ? `${obs.speed} km/h` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
