'use client';

// ==============================================================================
// Aviation Monitoring & Analytics Platform — Favorite Flights Page
// ==============================================================================
// Menampilkan daftar penerbangan yang telah disimpan oleh pengguna aktif.

import React, { useState } from 'react';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getFavorites, removeFavorite } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { Bookmark, Trash2, ArrowRight, Plane, Calendar, AlertCircle } from 'lucide-react';

export default function FavoritesPage() {
  const queryClient = useQueryClient();
  const { user, loading: authLoading } = useAuth();
  const [feedback, setFeedback] = useState<string | null>(null);

  const {
    data: favorites,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['favorites'],
    queryFn: getFavorites,
    enabled: !!user,
  });

  const deleteMutation = useMutation({
    mutationFn: (favoriteId: string) => removeFavorite(favoriteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
      setFeedback('Penerbangan berhasil dihapus dari daftar favorit.');
      setTimeout(() => setFeedback(null), 3000);
    },
    onError: (err: any) => {
      setFeedback(err?.message || 'Gagal menghapus favorit');
      setTimeout(() => setFeedback(null), 3000);
    },
  });

  if (authLoading) {
    return (
      <div className="flex justify-center items-center min-h-[300px]">
        <div className="w-8 h-8 border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="glass-panel p-10 rounded-2xl text-center max-w-md mx-auto space-y-4">
        <Bookmark className="w-12 h-12 text-slate-500 mx-auto" />
        <h2 className="text-xl font-bold text-white">Login Diperlukan</h2>
        <p className="text-sm text-slate-400">
          Silakan masuk ke akun Anda untuk melihat dan mengelola daftar penerbangan favorit.
        </p>
        <Link
          href="/login"
          className="inline-block px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm transition-colors"
        >
          Masuk Sekarang
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <Bookmark className="w-7 h-7 text-amber-400 fill-amber-400" />
          Penerbangan Favorit Saya
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Daftar penerbangan yang Anda simpan untuk pemantauan rute dan jadwal prioritas.
        </p>
      </div>

      {feedback && (
        <div className="p-3.5 rounded-xl bg-cyan-950/90 border border-cyan-500/40 text-cyan-200 text-sm flex items-center justify-between">
          <span>{feedback}</span>
          <button onClick={() => setFeedback(null)} className="text-cyan-400 hover:text-white text-xs">
            Tutup
          </button>
        </div>
      )}

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="glass-panel p-6 rounded-2xl animate-pulse space-y-4">
              <div className="h-5 bg-slate-800 rounded w-1/3" />
              <div className="h-10 bg-slate-800 rounded" />
            </div>
          ))}
        </div>
      )}

      {isError && (
        <div className="glass-panel p-6 rounded-2xl text-center text-rose-400 space-y-2">
          <AlertCircle className="w-8 h-8 mx-auto" />
          <p className="text-sm">{(error as Error)?.message}</p>
        </div>
      )}

      {!isLoading && !isError && (!favorites || favorites.length === 0) && (
        <div className="glass-panel p-12 rounded-2xl text-center space-y-4 max-w-md mx-auto">
          <Bookmark className="w-12 h-12 text-slate-600 mx-auto" />
          <h2 className="text-lg font-bold text-white">Belum Ada Favorit</h2>
          <p className="text-xs text-slate-400">
            Anda belum menambahkan penerbangan ke favorit. Klik tombol &ldquo;Simpan&rdquo; pada kartu penerbangan di menu eksplorasi.
          </p>
          <Link
            href="/flights"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm text-cyan-400 font-medium transition-colors"
          >
            Cari Penerbangan
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}

      {!isLoading && !isError && favorites && favorites.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {favorites.map((fav) => {
            const flight = fav.flight;
            if (!flight) return null;
            return (
              <div
                key={fav.id}
                className="glass-panel glass-panel-hover p-5 rounded-2xl flex flex-col justify-between space-y-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xl font-black font-mono text-cyan-400 block">
                      {flight.flight_number}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">
                      {flight.airline_name || 'Maskapai Tidak Dikenal'}
                    </span>
                    <div className="flex items-center gap-1 text-[11px] text-slate-400 mt-0.5">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      <span>{flight.flight_date}</span>
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-slate-800 text-cyan-300 border border-slate-700">
                    {flight.flight_status}
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xl font-extrabold font-mono text-white block">
                      {flight.departure_iata || '—'}
                    </span>
                    <span className="text-[11px] text-slate-400 truncate max-w-[100px] block">
                      {flight.departure_airport || 'Asal'}
                    </span>
                  </div>
                  <Plane className="w-4 h-4 text-cyan-400 transform rotate-90" />
                  <div className="text-right">
                    <span className="text-xl font-extrabold font-mono text-white block">
                      {flight.arrival_iata || '—'}
                    </span>
                    <span className="text-[11px] text-slate-400 truncate max-w-[100px] block">
                      {flight.arrival_airport || 'Tujuan'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                  <button
                    onClick={() => deleteMutation.mutate(fav.id)}
                    disabled={deleteMutation.isPending}
                    className="flex items-center gap-1.5 text-xs text-rose-400 hover:text-rose-300 font-medium transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Hapus
                  </button>

                  <Link
                    href={`/flights/${flight.id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
                  >
                    Lihat Rincian
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
