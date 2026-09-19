# ==============================================================================
# Aviation Monitoring & Analytics Platform — Frontend Dockerfile (Next.js 15)
# ==============================================================================
# Desain Multi-Stage Build untuk Optimalisasi Ukuran & Keamanan:
# 1. Stage 'deps': Menginstal dependensi melalui 'npm ci' berbasis package-lock.json.
# 2. Stage 'builder': Mengompilasi kode Next.js (type-checking, bundling, static generation).
# 3. Stage 'runner': Image runtime minimal menggunakan 'standalone' output Next.js
#    sehingga tidak perlu menyertakan seluruh node_modules berukuran ratusan MB.
# 4. Non-root user 'nextjs': Mencegah proses aplikasi berjalan dengan hak akses root.

FROM node:22-alpine AS base

# --- Tahap 1: Dependencies ---
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# --- Tahap 2: Builder ---
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Menonaktifkan telemetri Next.js saat build untuk privasi dan kecepatan
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# --- Tahap 3: Runner (Production Runtime) ---
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Buat grup dan pengguna non-root
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Salin aset publik dan folder .next
COPY --from=builder /app/public ./public 2>/dev/null || true
RUN mkdir .next && chown nextjs:nodejs .next

# Salin output standalone dan static chunks
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
