import React from 'react';
import Link from 'next/link';
import { Plane, BarChart3, Search, ShieldCheck, Zap, ArrowRight } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="space-y-16 py-8">
      {/* Hero Section */}
      <section className="text-center max-w-3xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          Live Flight Data & Observability
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
          Pemantauan & Analitik Penerbangan{' '}
          <span className="bg-gradient-to-r from-cyan-400 via-teal-400 to-blue-500 bg-clip-text text-transparent">
            Berstandar Produksi
          </span>
        </h1>
        <p className="text-base sm:text-lg text-slate-400 leading-relaxed">
          Mengintegrasikan data penerbangan dari <strong>Aviationstack API</strong> melalui arsitektur
          modular monolith yang aman. Dilengkapi caching ephemeral Redis, rekam jejak telemetri historis,
          dan keamanan token berbasis HttpOnly cookie.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link
            href="/flights"
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold shadow-lg shadow-cyan-500/25 transition-all"
          >
            <Search className="w-4 h-4" />
            Eksplorasi Penerbangan
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 font-semibold border border-slate-700 transition-all"
          >
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            Buka Dashboard
          </Link>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel glass-panel-hover p-6 rounded-2xl space-y-3">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Zap className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-white">Cache-Aside & Ephemeral Redis</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Kueri pencarian dinormalisasi dan disimpan di Redis dengan TTL dinamis (3 menit untuk pesawat aktif, 2 jam untuk yang mendarat) guna melindungi batas kuota Aviationstack.
          </p>
        </div>

        <div className="glass-panel glass-panel-hover p-6 rounded-2xl space-y-3">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Plane className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-white">Rekam Jejak Telemetri Historis</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Menyimpan snapshot observasi berkala (koordinat, kecepatan, ketinggian) dalam tabel terpisah dengan indeks komposit untuk analisis pergerakan rute secara presisi.
          </p>
        </div>

        <div className="glass-panel glass-panel-hover p-6 rounded-2xl space-y-3">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-white">Keamanan Berlapis & HttpOnly Cookie</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            API key upstream terisolasi 100% di server backend. Token sesi dikirim melalui cookie HttpOnly dengan flag SameSite=Lax untuk mitigasi serangan XSS dan CSRF.
          </p>
        </div>
      </section>
    </div>
  );
}
