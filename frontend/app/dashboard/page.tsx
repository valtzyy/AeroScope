'use client';

// ==============================================================================
// Aviation Monitoring & Analytics Platform — Analytics Dashboard
// ==============================================================================
// Dashboard metrik operasional dan analitik penerbangan terlacak.
//
// Alasan Desain & Terminologi:
// 1. Terminologi Terukur: Menggunakan istilah "Tracked Flights by Airline" dan
//    "Observed On-Time Rate" untuk menjaga kejujuran analisis data.
// 2. Data Scope Note: Memberitahu pengguna bahwa statistik didasarkan pada sampel data
//    yang telah dilacak dan tersimpan di database lokal.

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAnalyticsOverview } from '@/lib/api';
import { Plane, CheckCircle2, Clock, XCircle, Info, RefreshCw } from 'lucide-react';

export default function DashboardPage() {
  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: getAnalyticsOverview,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
        <p className="text-sm text-slate-400">Memuat metrik analitik penerbangan...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="glass-panel p-8 rounded-2xl text-center max-w-lg mx-auto space-y-4 border-rose-500/30">
        <XCircle className="w-12 h-12 text-rose-400 mx-auto" />
        <h2 className="text-lg font-bold text-white">Gagal Memuat Analitik</h2>
        <p className="text-sm text-slate-400">
          {(error as Error)?.message || 'Terjadi kesalahan saat mengambil ringkasan analitik dari server.'}
        </p>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-medium text-slate-200 transition-colors"
        >
          Coba Lagi
        </button>
      </div>
    );
  }

  const { total_tracked_flights, status_distribution, delays, top_airlines, top_airports, data_scope_note } = data;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            Dashboard Analitik Penerbangan
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Ringkasan statistik agregat dari seluruh penerbangan yang terobservasi dalam sistem.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-sm font-medium text-slate-200 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 text-cyan-400 ${isFetching ? 'animate-spin' : ''}`} />
          Perbarui Data
        </button>
      </div>

      {/* Scope Disclaimer Banner */}
      <div className="flex items-start gap-3 p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/20 text-xs text-cyan-200 leading-relaxed">
        <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
        <p>{data_scope_note}</p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Tracked */}
        <div className="glass-panel p-5 rounded-2xl space-y-2">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Penerbangan Dilacak</span>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white">{total_tracked_flights}</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
              <Plane className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xs text-slate-400">Tersimpan dalam basis data lokal</p>
        </div>

        {/* Active Flights */}
        <div className="glass-panel p-5 rounded-2xl space-y-2">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Sedang Terbang (Active)</span>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-emerald-400">{status_distribution.active}</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <Plane className="w-4 h-4 animate-pulse" />
            </div>
          </div>
          <p className="text-xs text-slate-400">Pesawat dengan status aktif di udara</p>
        </div>

        {/* Landed Flights */}
        <div className="glass-panel p-5 rounded-2xl space-y-2">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Telah Mendarat (Landed)</span>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-blue-400">{status_distribution.landed}</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xs text-slate-400">Penerbangan yang telah sampai di tujuan</p>
        </div>

        {/* Observed On-Time Rate */}
        <div className="glass-panel p-5 rounded-2xl space-y-2">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Observed On-Time Rate</span>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-cyan-400">
              {delays.observed_on_time_rate_percent !== null ? `${delays.observed_on_time_rate_percent}%` : 'N/A'}
            </span>
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xs text-slate-400">
            {delays.total_evaluated_flights > 0
              ? `Dari ${delays.total_evaluated_flights} penerbangan mendarat`
              : 'Belum ada data penerbangan landed'}
          </p>
        </div>
      </div>

      {/* Two Column Layout: Status Distribution & Airlines */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Status Distribution Breakdown */}
        <div className="glass-panel p-6 rounded-2xl space-y-5">
          <h2 className="text-base font-bold text-white">Distribusi Status Penerbangan</h2>
          <div className="space-y-3">
            {[
              { label: 'Aktif (Active)', count: status_distribution.active, color: 'bg-emerald-500', text: 'text-emerald-400' },
              { label: 'Terjadwal (Scheduled)', count: status_distribution.scheduled, color: 'bg-amber-500', text: 'text-amber-400' },
              { label: 'Mendarat (Landed)', count: status_distribution.landed, color: 'bg-blue-500', text: 'text-blue-400' },
              { label: 'Dibatalkan (Cancelled)', count: status_distribution.cancelled, color: 'bg-rose-500', text: 'text-rose-400' },
              { label: 'Dialihkan / Insiden', count: status_distribution.diverted + status_distribution.incident, color: 'bg-purple-500', text: 'text-purple-400' },
            ].map((item) => {
              const pct = total_tracked_flights > 0 ? (item.count / total_tracked_flights) * 100 : 0;
              return (
                <div key={item.label} className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-300">{item.label}</span>
                    <span className={`font-mono font-medium ${item.text}`}>{item.count} penerbangan ({pct.toFixed(1)}%)</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                    <div className={`h-full ${item.color} rounded-full transition-all duration-500`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Tracked Flights by Airline */}
        <div className="glass-panel p-6 rounded-2xl space-y-5">
          <h2 className="text-base font-bold text-white">Penerbangan Terlacak Berdasarkan Maskapai</h2>
          {top_airlines.length === 0 ? (
            <p className="text-xs text-slate-500">Belum ada data maskapai tercatat.</p>
          ) : (
            <div className="space-y-4">
              {top_airlines.map((airline) => (
                <div key={airline.airline_name} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/50 border border-slate-700/60">
                  <div className="flex items-center gap-3">
                    <span className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 font-mono text-xs flex items-center justify-center font-bold">
                      {airline.airline_iata || '—'}
                    </span>
                    <div>
                      <p className="text-sm font-semibold text-slate-200">{airline.airline_name}</p>
                      <p className="text-xs text-slate-400 font-mono">{airline.percentage_of_tracked}% dari total terlacak</p>
                    </div>
                  </div>
                  <span className="text-sm font-mono font-bold text-slate-100">{airline.flight_count} flight</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Top Airports Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h2 className="text-base font-bold text-white">Bandara Paling Aktif (Hub Lalu Lintas Terlacak)</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-4">Kode IATA</th>
                <th className="py-3 px-4">Nama Bandara</th>
                <th className="py-3 px-4 text-center">Keberangkatan</th>
                <th className="py-3 px-4 text-center">Kedatangan</th>
                <th className="py-3 px-4 text-right">Total Aktivitas</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {top_airports.map((airport) => (
                <tr key={airport.airport_iata} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3.5 px-4 font-mono font-bold text-cyan-400">{airport.airport_iata}</td>
                  <td className="py-3.5 px-4">{airport.airport_name || 'Bandara Internasional'}</td>
                  <td className="py-3.5 px-4 text-center font-mono">{airport.departures_count}</td>
                  <td className="py-3.5 px-4 text-center font-mono">{airport.arrivals_count}</td>
                  <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-100">
                    {airport.departures_count + airport.arrivals_count}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
