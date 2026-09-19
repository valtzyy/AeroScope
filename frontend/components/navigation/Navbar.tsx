'use client';

// ==============================================================================
// Aviation Monitoring & Analytics Platform — Navigation Bar
// ==============================================================================
// Header navigasi utama dengan indikator status provider dan menu pengguna.

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Plane, BarChart3, Search, Bookmark, History, LogIn, LogOut, User as UserIcon } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { href: '/flights', label: 'Penerbangan', icon: Search },
    { href: '/favorites', label: 'Favorit', icon: Bookmark, authRequired: true },
    { href: '/history', label: 'Riwayat', icon: History, authRequired: true },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-aviation-border/80 bg-aviation-darker/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
              <Plane className="w-5 h-5 text-white transform -rotate-45" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-wider text-white flex items-center gap-1.5">
                AeroScope
                <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono">
                  v1.0
                </span>
              </span>
              <p className="text-[11px] text-slate-400 leading-none">Aviation Monitoring & Analytics</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              if (item.authRequired && !user) return null;
              const Icon = item.icon;
              const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-500/20'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* Auth / Profile Section */}
          <div className="flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700">
                  <UserIcon className="w-4 h-4 text-cyan-400" />
                  <span className="text-sm font-medium text-slate-200">{user.name}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-900/50 text-cyan-300 font-mono">
                    {user.role}
                  </span>
                </div>
                <button
                  onClick={() => logout()}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-rose-400 hover:bg-rose-500/10 border border-rose-500/20 transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden sm:inline">Keluar</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  href="/login"
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/80 transition-colors"
                >
                  <LogIn className="w-4 h-4" />
                  Masuk
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-1.5 rounded-lg text-sm font-medium bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-md shadow-cyan-500/20 transition-all"
                >
                  Daftar
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
