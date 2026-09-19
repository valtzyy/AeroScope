import type { Metadata } from 'next';
import './globals.css';
import { QueryProvider } from '@/lib/query-provider';
import { AuthProvider } from '@/lib/auth-context';
import { Navbar } from '@/components/navigation/Navbar';

export const metadata: Metadata = {
  title: 'AeroScope — Aviation Monitoring & Analytics Platform',
  description:
    'Platform analitik dan pemantauan data penerbangan terkini yang terintegrasi dengan Aviationstack API, dilengkapi caching ephemeral dan riwayat telemetri.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id" className="dark">
      <body className="bg-aviation-darker text-slate-100 min-h-screen flex flex-col">
        <QueryProvider>
          <AuthProvider>
            <Navbar />
            <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {children}
            </main>
            <footer className="border-t border-aviation-border/60 bg-aviation-dark py-6 text-center text-xs text-slate-500">
              <p>
                © {new Date().getFullYear()} AeroScope Platform. Terintegrasi dengan Aviationstack API.
                Dibangun dengan standar produksi Next.js, FastAPI, PostgreSQL, dan Redis.
              </p>
            </footer>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
