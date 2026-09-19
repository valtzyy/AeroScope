'use client';

// ==============================================================================
// Aviation Monitoring & Analytics Platform — TanStack Query Provider
// ==============================================================================
// Mengelola caching di sisi client (frontend cache) untuk mengurangi re-fetch berlebih.

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 menit sebelum data dianggap stale
            refetchOnWindowFocus: false, // Mencegah refetch agresif yang menghabiskan kuota
            retry: 1,
          },
        },
      })
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
