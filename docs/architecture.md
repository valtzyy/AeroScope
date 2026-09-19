# Arsitektur Sistem — Aviation Monitoring & Analytics Platform

Dokumen ini menjelaskan arsitektur tingkat tinggi, komponen sistem, pemisahan tanggung jawab (separation of concerns), aliran data (*data flow*), strategi caching, serta kontrol keamanan pada **Aviation Monitoring & Analytics Platform**.

---

## 1. Ikhtisar Arsitektur

Platform ini dibangun menggunakan pola **Modular Monolith** dengan arsitektur berlapis (*layered architecture*). Desain ini dipilih untuk mempermudah pengembangan, pengujian, dan pemeliharaan tanpa kompleksitas operasional microservices (seperti distributed tracing, network latency, atau distributed transaction), namun tetap menjaga batas modularitas yang sangat rapi dan siap dipisahkan di masa depan jika beban trafik meningkat.

```mermaid
graph TD
    Client["Browser / Frontend Client (Next.js 15)"]
    
    subgraph Edge & Security
        Nginx["Reverse Proxy / Edge"]
        RateLimiter["Slowapi Rate Limiter (Token Bucket)"]
        AuthMiddleware["JWT Cookie Verifier (HttpOnly/SameSite)"]
    end

    subgraph Backend Application ["FastAPI Modular Monolith"]
        Router["API Router (v1 Endpoints)"]
        ServiceLayer["Service Layer (Domain Business Logic)"]
        RepoLayer["Repository Layer (SQLAlchemy ORM)"]
        ProviderLayer["Flight Provider Adapter"]
    end

    subgraph Infrastructure
        RedisCache[("Redis 7 Cache (Ephemeral In-Memory)")]
        PostgresDB[("PostgreSQL 16 Relational DB")]
        ExtAPI["Aviationstack External API"]
    end

    Client -->|HTTPS + HttpOnly Cookie| Edge
    Edge --> RateLimiter
    RateLimiter --> AuthMiddleware
    AuthMiddleware --> Router
    Router --> ServiceLayer
    
    ServiceLayer -->|1. Check / Write Cache| RedisCache
    ServiceLayer -->|2. Query / Persist Entity| RepoLayer
    ServiceLayer -->|3. Fetch Remote Flights| ProviderLayer
    
    RepoLayer -->|Parameterized SQL| PostgresDB
    ProviderLayer -->|Bounded Retries & Abort on 429| ExtAPI
```

---

## 2. Lapisan Sistem (System Layers)

Sistem dibagi menjadi lapisan-lapisan independen dengan aturan dependensi satu arah (*unidirectional dependency*):

### A. Presentation Layer (Frontend — Next.js 15 App Router)
- **Teknologi**: Next.js 15, React 19, TypeScript, Tailwind CSS, Lucide Icons, TanStack React Query.
- **Tanggung Jawab**:
  - Menyajikan antarmuka pengguna responsif dengan estetika dark mode bernuansa kokpit penerbangan modern.
  - State management asinkron menggunakan TanStack React Query (`stale-while-revalidate`), mengurangi re-fetch yang berlebihan.
  - Autentikasi transparan via HttpOnly cookies (`credentials: 'include'`), sehingga kode JavaScript di browser tidak menyentuh token JWT.

### B. Transport & Gateway Layer (FastAPI Router & Middlewares)
- **Teknologi**: FastAPI, Slowapi, Starlette Middlewares.
- **Tanggung Jawab**:
  - Serialisasi dan deserialisasi data request/response berbasis skema Pydantic v2 yang ketat.
  - Proteksi laju permintaan (*rate limiting*) berbasis IP client untuk mencegah *denial of service* dan *credential stuffing*.
  - Menolak *payload* yang tidak valid sebelum menyentuh lapisan logika bisnis (*fail-fast input validation*).
  - Formatting response terstandarisasi: `{ "data": ..., "meta": ..., "error": ... }`.

### C. Domain & Service Layer
- **Tanggung Jawab**:
  - Mengorkestrasi aturan bisnis (misalnya: alur pencarian penerbangan dengan strategi cache-aside).
  - Menghitung metrik observasi telemetri (snapshot posisi, kecepatan horizontal/vertikal, altitude).
  - Menghitung analitik operasional agregat dengan label jujur (*Tracked Flights by Airline*, *Observed On-Time Rate*).
  - Melindungi hak akses objek pengguna (*mitigasi IDOR*).

### D. Provider Adapter Layer (External API Abstraction)
- **Tanggung Jawab**:
  - Mengisolasi dependensi vendor pihak ketiga (Aviationstack) menggunakan interface abstrak `FlightDataProvider`.
  - Mengonversi skema respon pihak ketiga yang rapuh atau inkonsisten ke Domain DTO yang kuat dan stabil via `FlightMapper`.
  - Menangani kegagalan jaringan dengan strategi *exponential backoff with jitter* dan *circuit-breaker* sederhana (segera membatalkan request saat kuota habis / HTTP 429).
  - Menyediakan `MockFlightProvider` deterministik untuk pengujian offline dan penghematan kuota gratis.

### E. Persistence Layer (PostgreSQL 16 & Ephemeral Redis 7)
- **PostgreSQL 16**:
  - Sumber kebenaran tunggal (*Single Source of Truth*) untuk data pengguna, penerbangan tersimpan, riwayat pencarian, daftar favorit, dan snapshot observasi telemetri.
  - Integritas relasional dengan *Foreign Key CASCADE* dan *Unique Constraints* (`(flight_number, flight_date, departure_iata, arrival_iata)`).
  - Pengindeksan komposit untuk kueri deret waktu (*time-series timeline*).
- **Redis 7 (Ephemeral)**:
  - Cache kueri pencarian penerbangan berbasis SHA-256 hash.
  - Cache analitik agregat (TTL 60 detik).
  - Berjalan dalam mode murni in-memory (`--save "" --appendonly no`) tanpa beban I/O disk yang tidak perlu.

---

## 3. Aliran Data Utama (End-to-End Data Flow)

### Skenario: Pencarian Penerbangan (Search Flight Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Pengguna / Browser
    participant API as FastAPI Router
    participant Service as FlightService
    participant Cache as Redis (Ephemeral)
    participant Provider as FlightDataProvider
    participant Repo as FlightRepository
    participant DB as PostgreSQL 16

    User->>API: GET /api/v1/flights?flight_number=GA401&date=2026-09-18
    API->>Service: search_flights(query)
    
    Service->>Cache: get(sha256_cache_key)
    alt Cache Hit (Data Ditemukan di Redis)
        Cache-->>Service: Serialized JSON
        Service-->>API: FlightListResponse (source: cache)
        API-->>User: 200 OK
    else Cache Miss (Data Belum Dicache)
        Service->>Provider: search_flights(query)
        Provider-->>Service: List[FlightDTO]
        
        Service->>Repo: upsert_flights(flights)
        Repo->>DB: INSERT ... ON CONFLICT (flight_number, date, route) DO UPDATE
        DB-->>Repo: Saved Entities
        
        Service->>Cache: setex(sha256_cache_key, dynamic_ttl, json_data)
        Service-->>API: FlightListResponse (source: provider)
        API-->>User: 200 OK
    end
```

---

## 4. Keamanan & Proteksi Data

1. **Otentikasi Aman**:
   - Token JWT ditransmisikan hanya via cookie ber-atribut `HttpOnly=True`, `SameSite=Lax`, dan `Secure=True` (di production).
   - Menghilangkan sepenuhnya celah pencurian token melalui serangan Cross-Site Scripting (XSS).
2. **Hashing Password Kuat**:
   - Menggunakan algoritma **Argon2id**, standar industri modern yang tahan terhadap serangan GPU cracking dan time-memory trade-off attacks.
3. **Mitigasi IDOR (Insecure Direct Object Reference)**:
   - Setiap penghapusan atau modifikasi data (favorit, history pencarian) memvalidasi `WHERE id = :target_id AND user_id = :current_user_id` secara ketat di repository SQL.
4. **Proteksi Kredensial**:
   - Filter logging mendeteksi dan menyamarkan API keys, password, dan token JWT (`***MASKED***`) sebelum dicetak ke log stream.
   - Pydantic Settings menolak startup aplikasi jika kredensial produksi tidak memenuhi standar keamanan (*fail-fast*).
