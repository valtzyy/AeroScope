'use client';

// ==============================================================================
// Aviation Monitoring & Analytics Platform — Authentication Context
// ==============================================================================
// React Context untuk mengelola status sesi login pengguna di seluruh komponen frontend.
//
// Alasan Arsitektur:
// Saat aplikasi dimuat, context ini memanggil /api/v1/auth/me untuk memeriksa apakah
// browser memiliki cookie sesi aktif yang valid. Tidak ada token yang disimpan di localStorage.

import React, { createContext, useContext, useEffect, useState } from 'react';
import { getCurrentUser, loginUser, logoutUser, registerUser } from './api';
import { User } from './types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Periksa sesi pengguna aktif saat pertama kali aplikasi dibuka di browser
  useEffect(() => {
    async function loadUserSession() {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        // Pengguna belum login atau cookie kedaluwarsa
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    loadUserSession();
  }, []);

  const login = async (email: string, pass: string) => {
    const loggedUser = await loginUser(email, pass);
    setUser(loggedUser);
  };

  const register = async (email: string, pass: string, name: string) => {
    const newUser = await registerUser(email, pass, name);
    setUser(newUser);
  };

  const logout = async () => {
    try {
      await logoutUser();
    } finally {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth harus digunakan di dalam AuthProvider');
  }
  return context;
}
