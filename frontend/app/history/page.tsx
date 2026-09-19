'use client';

// ==============================================================================
// Aviation Monitoring & Analytics Platform — Search History Page
// ==============================================================================
// Menampilkan riwayat pencarian pengguna dengan filter dan opsi pencarian ulang instan.

import React, { useState } from 'react';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { deleteSearchHistory, getSearchHistory } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { History, Trash2, Search, ArrowRight, Clock, AlertCircle } from 'lucide-react';

export default function SearchHistoryPage() {
  const queryClient = useQueryClient();
  const { user, loading: authLoading } = useAuth();
  const [page, setPage] = useState(1);
  const [feedback, setFeedback] = useState<string | null>(null);

  const {
    data: response,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['search-history', page],
    queryFn: () => getSearchHistory(page, 20),
    enabled: !!user,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteSearchHistory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['search-history'] });
      setFeedback('Riwayat pencarian berhasil dihapus.');
      setTimeout(() => setFeedback(null), 3000);
    },
    onError: (err: any) => {
      setFeedback(err?.message || 'Gagal menghapus entri riwayat');
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
        <History className="w-12 h-12 text-slate-500 mx-auto" />
        <h2 className="text-xl font-bold text-white">Login Diperlukan</h2>
        <p className="text-sm text-slate-400">
          Silakan login ke akun Anda untuk melihat jejak audit riwayat pencarian Anda.
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

  const formatDateTime = (iso: string) => {
    try {
      return new Date(iso).toLocaleString('id-ID', {
        dateStyle: 'medium',
        timeStyle: 'short',
      });
    } catch {
      return iso;
    }
  };

  const historyItems = response?.data || [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <History className="w-7 h-7 text-cyan-400" />
          Riwayat Pencarian
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Daftar kueri pencarian yang pernah Anda lakukan, lengkap dengan parameter filter dan waktu pencarian.
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
        <div className="glass-panel p-8 rounded-2xl animate-pulse space-y-3">
          <div className="h-6 bg-slate-800 rounded w-1/4" />
          <div className="h-12 bg-slate-800 rounded" />
          <div className="h-12 bg-slate-800 rounded" />
        </div>
      )}

      {isError && (
        <div className="glass-panel p-6 rounded-2xl text-center text-rose-400 space-y-2">
          <AlertCircle className="w-8 h-8 mx-auto" />
          <p className="text-sm">{(error as Error)?.message}</p>
        </div>
      )}

      {!isLoading && !isError && historyItems.length === 0 && (
        <div className="glass-panel p-12 rounded-2xl text-center space-y-4 max-w-md mx-auto">
          <History className="w-12 h-12 text-slate-600 mx-auto" />
          <h2 className="text-lg font-bold text-white">Belum Ada Riwayat</h2>
          <p className="text-xs text-slate-400">
            Pencarian penerbangan yang Anda lakukan saat login akan otomatis tersimpan di sini.
          </p>
          <Link
            href="/flights"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm text-cyan-400 font-medium transition-colors"
          >
            Mulai Mencari
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}

      {!isLoading && !isError && historyItems.length > 0 && (
        <div className="glass-panel rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider bg-slate-900/50">
                  <th className="py-3.5 px-4">Waktu Pencarian</th>
                  <th className="py-3.5 px-4">Parameter Kueri</th>
                  <th className="py-3.5 px-4 text-center">Hasil Ditemukan</th>
                  <th className="py-3.5 px-4 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {historyItems.map((item) => {
                  const params = item.query_parameters || {};
                  return (
                    <tr key={item.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3.5 px-4 text-xs text-slate-400 font-mono">
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-slate-500" />
                          <span>{formatDateTime(item.searched_at)}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex flex-wrap gap-1.5">
                          {Object.entries(params).map(([k, v]) => {
                            if (!v) return null;
                            return (
                              <span
                                key={k}
                                className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[11px] font-mono text-cyan-300"
                              >
                                {k}: <strong className="text-white">{String(v)}</strong>
                              </span>
                            );
                          })}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center font-mono font-bold text-slate-200">
                        {item.result_count}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => deleteMutation.mutate(item.id)}
                          disabled={deleteMutation.isPending}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                          title="Hapus Riwayat Ini"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
