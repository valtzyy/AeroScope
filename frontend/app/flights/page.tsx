'use client';

// ==============================================================================
// Aviation Monitoring & Analytics Platform — Flight Search & Explorer
// ==============================================================================
// Halaman penjelajahan dan pencarian multi-kriteria penerbangan dengan cache-aside.

import React, { useState } from 'react';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { addFavorite, searchFlights } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { Flight } from '@/lib/types';
import {
  Search,
  Plane,
  ArrowRight,
  Bookmark,
  Calendar,
  Clock,
  MapPin,
  ChevronLeft,
  ChevronRight,
  Check,
  AlertCircle,
} from 'lucide-react';

export default function FlightsPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  // Form State
  const [flightNumber, setFlightNumber] = useState('');
  const [airline, setAirline] = useState('');
  const [depIata, setDepIata] = useState('');
  const [arrIata, setArrIata] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);

  // Active filter state used for query
  const [appliedFilters, setAppliedFilters] = useState({
    flight_number: '',
    airline: '',
    dep_iata: '',
    arr_iata: '',
    flight_status: '',
    page: 1,
    limit: 12,
  });

  const [savedFlightIds, setSavedFlightIds] = useState<Set<string>>(new Set());
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  // Query flights
  const { data, isLoading, isError, error, isFetching } = useQuery({
    queryKey: ['flights', appliedFilters],
    queryFn: () => searchFlights(appliedFilters),
  });

  // Mutation to add favorite
  const favoriteMutation = useMutation({
    mutationFn: (flightId: string) => addFavorite(flightId),
    onSuccess: (_, flightId) => {
      setSavedFlightIds((prev) => new Set(prev).add(flightId));
      setActionMessage('Penerbangan berhasil disimpan ke favorit!');
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
      setTimeout(() => setActionMessage(null), 3000);
    },
    onError: (err: any) => {
      setActionMessage(err?.message || 'Gagal menyimpan ke favorit');
      setTimeout(() => setActionMessage(null), 3000);
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setAppliedFilters({
      flight_number: flightNumber.trim(),
      airline: airline.trim(),
      dep_iata: depIata.trim().toUpperCase(),
      arr_iata: arrIata.trim().toUpperCase(),
      flight_status: status,
      page: 1,
      limit: 12,
    });
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    setAppliedFilters((prev) => ({ ...prev, page: newPage }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getStatusBadge = (flightStatus: string) => {
    switch (flightStatus.toLowerCase()) {
      case 'active':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Aktif (Airborne)
          </span>
        );
      case 'scheduled':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <Clock className="w-3 h-3" />
            Terjadwal
          </span>
        );
      case 'landed':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/15 text-blue-400 border border-blue-500/30">
            <Check className="w-3 h-3" />
            Mendarat
          </span>
        );
      case 'cancelled':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <AlertCircle className="w-3 h-3" />
            Dibatalkan
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-700/50 text-slate-300 border border-slate-600">
            {flightStatus}
          </span>
        );
    }
  };

  const formatTime = (isoString?: string | null) => {
    if (!isoString) return 'Not available';
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' });
    } catch {
      return 'Not available';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Eksplorasi Penerbangan
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Cari dan pantau data penerbangan internasional & domestik dengan sistem caching teroptimasi.
        </p>
      </div>

      {/* Action Notification */}
      {actionMessage && (
        <div className="p-3.5 rounded-xl bg-cyan-950/80 border border-cyan-500/40 text-cyan-200 text-sm flex items-center justify-between animate-fadeIn">
          <span>{actionMessage}</span>
          <button onClick={() => setActionMessage(null)} className="text-cyan-400 hover:text-white text-xs">
            Tutup
          </button>
        </div>
      )}

      {/* Multi-Criteria Filter Panel */}
      <form onSubmit={handleSearch} className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Flight Number */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Nomor Penerbangan</label>
            <input
              type="text"
              placeholder="Contoh: DL415"
              value={flightNumber}
              onChange={(e) => setFlightNumber(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white text-sm focus:outline-none focus:border-cyan-500 transition-colors font-mono"
            />
          </div>

          {/* Airline */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Nama Maskapai</label>
            <input
              type="text"
              placeholder="Contoh: Delta / Garuda"
              value={airline}
              onChange={(e) => setAirline(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white text-sm focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          {/* Departure Airport IATA */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Bandara Asal (IATA)</label>
            <input
              type="text"
              placeholder="Contoh: SFO / CGK"
              maxLength={4}
              value={depIata}
              onChange={(e) => setDepIata(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white text-sm focus:outline-none focus:border-cyan-500 transition-colors font-mono uppercase"
            />
          </div>

          {/* Arrival Airport IATA */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Bandara Tujuan (IATA)</label>
            <input
              type="text"
              placeholder="Contoh: JFK / DPS"
              maxLength={4}
              value={arrIata}
              onChange={(e) => setArrIata(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white text-sm focus:outline-none focus:border-cyan-500 transition-colors font-mono uppercase"
            />
          </div>

          {/* Status Dropdown */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Status Penerbangan</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white text-sm focus:outline-none focus:border-cyan-500 transition-colors"
            >
              <option value="">Semua Status</option>
              <option value="active">Sedang Terbang (Active)</option>
              <option value="scheduled">Terjadwal (Scheduled)</option>
              <option value="landed">Telah Mendarat (Landed)</option>
              <option value="cancelled">Dibatalkan (Cancelled)</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={isFetching}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-sm font-semibold shadow-md shadow-cyan-500/20 transition-all disabled:opacity-50"
          >
            <Search className="w-4 h-4" />
            {isFetching ? 'Mencari...' : 'Terapkan Filter'}
          </button>
        </div>
      </form>

      {/* Freshness Bar */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400" />
          Live Flight Data — Terkoneksi ke Backend FastAPI
        </span>
        {data && <span>Menampilkan total {data.meta.total} penerbangan ditemukan</span>}
      </div>

      {/* Results Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="glass-panel p-6 rounded-2xl animate-pulse space-y-4">
              <div className="h-5 bg-slate-800 rounded w-1/3" />
              <div className="h-8 bg-slate-800 rounded w-2/3" />
              <div className="h-4 bg-slate-800 rounded w-full" />
            </div>
          ))}
        </div>
      )}

      {/* Results Error State */}
      {isError && (
        <div className="glass-panel p-8 rounded-2xl text-center space-y-3 border-rose-500/30">
          <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
          <h2 className="text-base font-bold text-white">Gagal Mengambil Data</h2>
          <p className="text-xs text-slate-400">{(error as Error)?.message}</p>
        </div>
      )}

      {/* Results Empty State */}
      {!isLoading && !isError && data?.data.length === 0 && (
        <div className="glass-panel p-12 rounded-2xl text-center space-y-3 max-w-md mx-auto">
          <Plane className="w-12 h-12 text-slate-600 mx-auto" />
          <h2 className="text-lg font-bold text-white">Penerbangan Tidak Ditemukan</h2>
          <p className="text-xs text-slate-400">
            Tidak ada data penerbangan yang cocok dengan parameter filter Anda. Coba sesuaikan nomor atau kode bandara.
          </p>
        </div>
      )}

      {/* Flight Cards Grid */}
      {!isLoading && !isError && data && data.data.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {data.data.map((flight: Flight) => {
            const isSaved = savedFlightIds.has(flight.id);
            return (
              <div
                key={flight.id}
                className="glass-panel glass-panel-hover p-5 rounded-2xl flex flex-col justify-between space-y-4"
              >
                {/* Card Header: Flight Number, Airline, Status */}
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-black font-mono tracking-wide text-cyan-400">
                        {flight.flight_number}
                      </span>
                      <span className="text-xs text-slate-400 font-medium">
                        {flight.airline_name || 'Maskapai Tidak Dikenal'}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 text-[11px] text-slate-400 mt-0.5">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      <span>{flight.flight_date}</span>
                    </div>
                  </div>
                  {getStatusBadge(flight.flight_status)}
                </div>

                {/* Route Path Visual */}
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                  {/* Origin */}
                  <div className="text-left">
                    <span className="text-xl font-extrabold font-mono text-white block">
                      {flight.departure_iata || '—'}
                    </span>
                    <span className="text-[11px] text-slate-400 truncate max-w-[100px] block">
                      {flight.departure_airport || 'Asal'}
                    </span>
                    <span className="text-[10px] text-cyan-300/80 font-mono mt-0.5 block">
                      {formatTime(flight.departure_scheduled)}
                    </span>
                  </div>

                  {/* Route Line with Plane */}
                  <div className="flex-1 px-4 flex flex-col items-center">
                    <Plane className="w-4 h-4 text-cyan-400 mb-1 transform rotate-90" />
                    <div className="w-full h-0.5 bg-gradient-to-r from-cyan-500/20 via-cyan-400 to-cyan-500/20" />
                    <span className="text-[10px] text-slate-400 mt-1">Langsung</span>
                  </div>

                  {/* Destination */}
                  <div className="text-right">
                    <span className="text-xl font-extrabold font-mono text-white block">
                      {flight.arrival_iata || '—'}
                    </span>
                    <span className="text-[11px] text-slate-400 truncate max-w-[100px] block">
                      {flight.arrival_airport || 'Tujuan'}
                    </span>
                    <span className="text-[10px] text-cyan-300/80 font-mono mt-0.5 block">
                      {formatTime(flight.arrival_scheduled)}
                    </span>
                  </div>
                </div>

                  {/* Card Footer: Detail Link & Favorite Button */}
                  <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                    <button
                      onClick={() => {
                        if (!user) {
                          setActionMessage('Silakan masuk (login) terlebih dahulu untuk menyimpan penerbangan ke favorit.');
                          setTimeout(() => setActionMessage(null), 3500);
                          return;
                        }
                        favoriteMutation.mutate(flight.id);
                      }}
                      disabled={isSaved || favoriteMutation.isPending}
                      className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                        isSaved
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                          : 'text-slate-400 hover:text-amber-400 hover:bg-slate-800'
                      }`}
                      title={user ? 'Simpan ke Favorit' : 'Masuk untuk menyimpan ke favorit'}
                    >
                      <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-amber-400' : ''}`} />
                      <span>{isSaved ? 'Tersimpan' : 'Simpan'}</span>
                    </button>

                  <Link
                    href={`/flights/${flight.id}`}
                    className="ml-auto inline-flex items-center gap-1 text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
                  >
                    Lihat Detail
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination Controls */}
      {!isLoading && !isError && data && data.meta.total_pages > 1 && (
        <div className="flex items-center justify-center gap-4 pt-4">
          <button
            onClick={() => handlePageChange(page - 1)}
            disabled={page <= 1 || isFetching}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
            Sebelumnya
          </button>
          <span className="text-xs text-slate-400 font-mono">
            Halaman {data.meta.page} dari {data.meta.total_pages}
          </span>
          <button
            onClick={() => handlePageChange(page + 1)}
            disabled={page >= data.meta.total_pages || isFetching}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Berikutnya
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
