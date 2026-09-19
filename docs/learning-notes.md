# Buku Catatan Rekayasa Perangkat Lunak (Software Engineering Learning Notes)

> **Catatan untuk Pengembang**: Dokumen ini dirancang sebagai panduan pembelajaran (*learning handbook*) komprehensif. Dokumen ini menjelaskan prinsip-prinsip arsitektur, pola desain, keamanan, dan keputusan rekayasa perangkat lunak yang diimplementasikan dalam **Aviation Monitoring & Analytics Platform**.

---

## Daftar Isi Konsep Pembelajaran

1. [Cache-Aside Pattern (Pola Cache di Samping)](#1-cache-aside-pattern)
2. [Provider Abstraction & Strategy Pattern](#2-provider-abstraction--strategy-pattern)
3. [Ephemeral In-Memory Cache vs Persistent Storage](#3-ephemeral-in-memory-cache-vs-persistent-storage)
4. [Idempotent Upsert (ON CONFLICT DO UPDATE)](#4-idempotent-upsert-on-conflict-do-update)
5. [Database Connection Pooling](#5-database-connection-pooling)
6. [Time-Series Telemetry & Composite Indexes](#6-time-series-telemetry--composite-indexes)
7. [Rate Limiting (Token Bucket Algorithm)](#7-rate-limiting-token-bucket-algorithm)
8. [HttpOnly & SameSite Cookies vs LocalStorage untuk JWT](#8-httponly--samesite-cookies-vs-localstorage-untuk-jwt)
9. [Argon2id Password Hashing](#9-argon2id-password-hashing)
10. [Role-Based Access Control (RBAC) di Backend](#10-role-based-access-control-rbac-di-backend)
11. [Fail-Fast Configuration & Pydantic Validation](#11-fail-fast-configuration--pydantic-validation)
12. [Structured Logging & Credential Masking](#12-structured-logging--credential-masking)
13. [Resilience: Bounded Exponential Backoff & 429 Short-Circuiting](#13-resilience-bounded-exponential-backoff--429-short-circuiting)
14. [In-Memory Telemetry & Operational Metrics](#14-in-memory-telemetry--operational-metrics)
15. [Boundary Defense: Raw Schema vs Domain DTO vs API Response](#15-boundary-defense-raw-schema-vs-domain-dto-vs-api-response)
16. [Modular Monolith Architecture](#16-modular-monolith-architecture)
17. [Docker Multi-Stage Build & Non-Root Containers](#17-docker-multi-stage-build--non-root-containers)
18. [Zero-Disk Redis Volume Architecture](#18-zero-disk-redis-volume-architecture)
19. [Alembic Declarative Database Versioning](#19-alembic-declarative-database-versioning)
20. [Next.js 15 App Router & Server/Client Components](#20-nextjs-15-app-router--serverclient-components)
21. [TanStack React Query: Stale-While-Revalidate](#21-tanstack-react-query-stale-while-revalidate)
22. [Dark Mode & Design Tokens dengan Tailwind CSS](#22-dark-mode--design-tokens-dengan-tailwind-css)
23. [Zero-SQLite Compromise: Real PostgreSQL in Tests](#23-zero-sqlite-compromise-real-postgresql-in-tests)
24. [Mitigasi IDOR (Insecure Direct Object Reference)](#24-mitigasi-idor-insecure-direct-object-reference)
25. [Analitik Jujur: 'Tracked Flights' vs 'Global Aviation'](#25-analitik-jujur-tracked-flights-vs-global-aviation)

---

### 1. Cache-Aside Pattern
- **Apa itu?**
  Pola di mana aplikasi bertanggung jawab langsung membaca data dari cache terlebih dahulu. Jika data tidak ada (*cache miss*), aplikasi membaca dari sumber data utama (database atau API eksternal), lalu menuliskan hasilnya ke dalam cache untuk request berikutnya dengan waktu kedaluwarsa (*Time-To-Live* / TTL).
- **Mengapa digunakan di project ini?**
  API pihak ketiga (Aviationstack) memiliki batas kuota bulanan gratis yang sangat terbatas (100–500 request) dan latensi jaringan yang cukup tinggi (500ms–2000ms).
- **Masalah apa yang diselesaikan?**
  Mengurangi beban panggilan berulang ke Aviationstack hingga >80%, menghemat kuota API, dan mempercepat waktu respon endpoint pencarian dari ~1.5 detik menjadi <15 milidetik untuk query yang sama.
- **Apa trade-off-nya?**
  Potensi data sedikit tertinggal (*stale data*) selama TTL cache masih aktif. Diminimalkan dengan menerapkan dynamic TTL (status aktif: 3 menit, scheduled: 15 menit, landed/cancelled: 120 menit).
- **Di mana kodenya dapat dipelajari?**
  - [cache_service.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/services/cache_service.py)
  - [flight_service.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/services/flight_service.py)

---

### 2. Provider Abstraction & Strategy Pattern
- **Apa itu?**
  Pola desain yang menyembunyikan implementasi spesifik vendor data di balik interface abstrak (`FlightDataProvider`), sehingga logika bisnis inti tidak terikat langsung pada struktur Aviationstack.
- **Mengapa digunakan di project ini?**
  Memisahkan dependensi eksternal agar platform dapat berganti provider (misalnya ke FlightAware, OpenSky, atau mock testing) tanpa mengubah satu baris pun di service layer.
- **Masalah apa yang diselesaikan?**
  Mencegah *vendor lock-in* dan memungkinkan pengujian lokal yang cepat tanpa perlu koneksi internet atau menghabiskan kuota API nyata.
- **Apa trade-off-nya?**
  Memerlukan penulisan lapisan konversi (*mapper*) tambahan untuk memetakan respon mentah ke Domain DTO.
- **Di mana kodenya dapat dipelajari?**
  - [base.py (FlightDataProvider)](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/clients/aviation/base.py)
  - [aviationstack.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/clients/aviation/aviationstack.py)
  - [mock_provider.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/clients/aviation/mock_provider.py)

---

### 3. Ephemeral In-Memory Cache vs Persistent Storage
- **Apa itu?**
  Pemisahan tegas peran penyimpanan data: Redis hanya berfungsi sebagai cache sementara di memori RAM, sedangkan PostgreSQL berfungsi sebagai sumber data permanen.
- **Mengapa digunakan di project ini?**
  Data penting pengguna (akun, favorit, riwayat pencarian, observasi) harus memiliki jaminan ACID dan durabilitas, sedangkan hasil kueri pencarian bersifat sementara dan bisa dibuat ulang kapan saja.
- **Masalah apa yang diselesaikan?**
  Mencegah hilangnya data penting pengguna saat Redis direstart, sekaligus menghindari penumpukan data kadaluwarsa pada database relasional.
- **Apa trade-off-nya?**
  Jika Redis mati atau di-flush, aplikasi mengalami *cache miss* sesaat namun sistem tetap berfungsi normal.
- **Di mana kodenya dapat dipelajari?**
  - [docker-compose.yml](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/docker-compose.yml)
  - [004-redis-ephemeral-cache.md](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/docs/adr/004-redis-ephemeral-cache.md)

---

### 4. Idempotent Upsert (ON CONFLICT DO UPDATE)
- **Apa itu?**
  Operasi database SQL yang secara atomik memasukkan baris baru (*INSERT*) atau memperbarui baris yang sudah ada (*UPDATE*) jika kunci unik yang ditentukan sudah ada.
- **Mengapa digunakan di project ini?**
  Ketika data penerbangan yang sama ditarik kembali dari provider eksternal, kita ingin memperbarui status terbaru (misal dari *scheduled* menjadi *active* atau *landed*) tanpa memicu error pelanggaran *duplicate key*.
- **Masalah apa yang diselesaikan?**
  Menghilangkan *race condition* antar kueri paralel dan mencegah duplikasi baris penerbangan.
- **Apa trade-off-nya?**
  Memerlukan *unique constraint* komposit yang dirancang dengan sangat hati-hati pada tabel database: `(flight_number, flight_date, departure_iata, arrival_iata)`.
- **Di mana kodenya dapat dipelajari?**
  - [flight_repository.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/repositories/flight_repository.py)
  - [database.md](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/docs/database.md)

---

### 5. Database Connection Pooling
- **Apa itu?**
  Mekanisme pemeliharaan sekumpulan koneksi database yang tetap terbuka (*connection pool*) dan dapat digunakan kembali oleh request yang masuk secara bergantian.
- **Mengapa digunakan di project ini?**
  Membuka dan menutup koneksi TCP PostgreSQL beserta proses handshake enkripsi SSL/TLS pada setiap HTTP request membutuhkan waktu sekitar 30–80ms per panggilan.
- **Masalah apa yang diselesaikan?**
  Mengurangi latensi kueri database secara drastis, membatasi konsumsi memori server PostgreSQL, dan mencegah server kehabisan koneksi (*connection starvation*).
- **Apa trade-off-nya?**
  Koneksi yang tidak dikembalikan ke pool (karena *leak* atau transaksi gantung) dapat memblokir request lain. Dicegah dengan penggunaan *context manager* async (`async with`).
- **Di mana kodenya dapat dipelajari?**
  - [session.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/db/session.py)

---

### 6. Time-Series Telemetry & Composite Indexes
- **Apa itu?**
  Tabel yang mencatat riwayat perubahan data berdasarkan waktu (*time-series snapshots*), seperti posisi GPS, ketinggian, dan kecepatan pesawat setiap kali diobservasi.
- **Mengapa digunakan di project ini?**
  Menyediakan riwayat pergerakan penerbangan untuk visualisasi grafik kronologis dan analisis tren keterlambatan.
- **Masalah apa yang diselesaikan?**
  Kueri `WHERE flight_id = :id ORDER BY observed_at DESC LIMIT 50` akan sangat lambat jika melakukan *full table scan* pada jutaan baris observasi.
- **Apa trade-off-nya?**
  Index komposit `(flight_id, observed_at DESC)` memakan ruang penyimpanan tambahan pada disk dan memperlambat sedikit proses INSERT observasi, namun mempercepat proses pembacaan data hingga ratusan kali lipat.
- **Di mana kodenya dapat dipelajari?**
  - [flight_observation.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/models/flight_observation.py)
  - [observation_repository.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/repositories/observation_repository.py)

---

### 7. Rate Limiting (Token Bucket Algorithm)
- **Apa itu?**
  Mekanisme pembatasan jumlah request yang diizinkan dari satu alamat IP client dalam kurun waktu tertentu (misalnya 10 request login per menit).
- **Mengapa digunakan di project ini?**
  Melindungi endpoint autentikasi dari serangan *brute-force* dan *credential stuffing*, serta melindungi endpoint refresh dari eksploitasi yang dapat menguras kuota Aviationstack.
- **Masalah apa yang diselesaikan?**
  Mencegah bot atau script jahat membanjiri server dengan jutaan request palsu (*Denial of Service*).
- **Apa trade-off-nya?**
  Pengguna di balik NAT atau proxy kantor yang sama mungkin berbagi batas limit IP yang sama. Dapat ditingkatkan ke rate limiting per-user ID setelah login.
- **Di mana kodenya dapat dipelajari?**
  - [rate_limit.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/core/rate_limit.py)
  - [auth.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/api/v1/routes/auth.py)
  - [flights.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/api/v1/routes/flights.py)

---

### 8. HttpOnly & SameSite Cookies vs LocalStorage untuk JWT
- **Apa itu?**
  Menyimpan token autentikasi JWT di dalam HTTP response cookie dengan flag `HttpOnly=True` dan `SameSite=Lax`, bukan menyimpannya di `window.localStorage` browser.
- **Mengapa digunakan di project ini?**
  `localStorage` dapat dibaca secara langsung oleh kode JavaScript mana pun di browser. Jika aplikasi memiliki celah XSS (*Cross-Site Scripting*) dari dependensi npm pihak ketiga, token pengguna dapat langsung dicuri.
- **Masalah apa yang diselesaikan?**
  Memberikan perlindungan penuh terhadap pencurian token JWT melalui serangan XSS karena browser menolak akses JavaScript ke cookie `HttpOnly`. Flag `SameSite=Lax` melindungi aplikasi dari serangan CSRF (*Cross-Site Request Forgery*).
- **Apa trade-off-nya?**
  Frontend harus menyertakan opsi `credentials: 'include'` pada setiap panggilan `fetch` API.
- **Di mana kodenya dapat dipelajari?**
  - [security.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/core/security.py)
  - [auth.py (routes)](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/api/v1/routes/auth.py)
  - [005-cookie-based-authentication.md](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/docs/adr/005-cookie-based-authentication.md)
  - [api.ts](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/frontend/lib/api.ts)

---

### 9. Argon2id Password Hashing
- **Apa itu?**
  Algoritma fungsi hashing kriptografi modern pemenang *Password Hashing Competition* (PHC) yang menggabungkan ketahanan terhadap serangan berbasis memori (Argon2d) dan serangan berbasis *side-channel* (Argon2i).
- **Mengapa digunakan di project ini?**
  Algoritma lama seperti MD5, SHA-256, atau bahkan bcrypt standar memiliki tingkat kerentanan yang lebih tinggi terhadap cracking menggunakan GPU ASIC modern berkekuatan komputasi masif.
- **Masalah apa yang diselesaikan?**
  Menjamin bahwa meskipun database berhasil diretas atau bocor, password asli pengguna tidak dapat dipulihkan dengan mudah menggunakan kamus kata (*rainbow table*) atau cluster GPU.
- **Apa trade-off-nya?**
  Memerlukan alokasi memori RAM dan waktu CPU yang lebih besar pada server saat menghitung hash (dikalibrasi dengan aman untuk 100ms per proses verifikasi).
- **Di mana kodenya dapat dipelajari?**
  - [security.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/core/security.py)

---

### 10. Role-Based Access Control (RBAC) di Backend
- **Apa itu?**
  Sistem pembatasan hak akses fitur berdasarkan peran pengguna (misalnya `USER` dan `ADMIN`).
- **Mengapa digunakan di project ini?**
  Mencegah pengguna biasa mengakses endpoint sensitif seperti pemantauan metrik operasional internal, kesehatan dependensi mendalam, atau manajemen data pengguna lain.
- **Masalah apa yang diselesaikan?**
  Mencegah pelanggaran *Privilege Escalation* di mana user biasa memodifikasi data administratif. Validasi wajib ditegakkan di backend, bukan hanya menyembunyikan tombol di frontend.
- **Apa trade-off-nya?**
  Setiap endpoint yang dilindungi memerlukan injeksi dependency `require_admin`.
- **Di mana kodenya dapat dipelajari?**
  - [dependencies.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/api/dependencies.py)

---

### 11. Fail-Fast Configuration & Pydantic Validation
- **Apa itu?**
  Prinsip di mana aplikasi sengaja menolak berjalan (*crash immediately on startup*) jika ada konfigurasi penting yang hilang, salah format, atau tidak aman.
- **Mengapa digunakan di project ini?**
  Mencegah aplikasi berjalan dalam kondisi bahaya tersembunyi (misalnya: berjalan di production dengan `JWT_SECRET` bawaan default development atau `FLIGHT_PROVIDER=mock`).
- **Masalah apa yang diselesaikan?**
  Menghilangkan *silent bugs* yang sering baru terdeteksi setelah aplikasi dideploy ke server produksi.
- **Apa trade-off-nya?**
  Aplikasi tidak akan menyala jika file `.env` belum dikonfigurasi dengan benar.
- **Di mana kodenya dapat dipelajari?**
  - [config.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/core/config.py)

---

### 12. Structured Logging & Credential Masking
- **Apa itu?**
  Format pencatatan log terstruktur berbasis JSON yang dilengkapi filter otomatis untuk menyensor informasi sensitif (API key, password, authorization token).
- **Mengapa digunakan di project ini?**
  Log aplikasi di server produksi sering diindeks oleh sistem pihak ketiga (Datadog, Elasticsearch, Loki). Kredensial yang tidak sengaja tercatat di log merupakan celah keamanan kritis (*CWE-532*).
- **Masalah apa yang diselesaikan?**
  Mencegah kebocoran rahasia sistem ke log file tanpa mengurangi kemampuan developer dalam men-debug aliran data request.
- **Apa trade-off-nya?**
  Menambah overhead pemrosesan string regex minimal sebelum log dicetak.
- **Di mana kodenya dapat dipelajari?**
  - [logging.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/core/logging.py)

---

### 13. Resilience: Bounded Exponential Backoff & 429 Short-Circuiting
- **Apa itu?**
  Pola penanganan kegagalan jaringan: jika panggilan API gagal karena *transient error* (misal timeout atau 502 Bad Gateway), aplikasi mencoba kembali dengan waktu jeda yang meningkat secara eksponensial (`1s, 2s, 4s...`) ditambah *jitter* acak. Namun jika server mengembalikan HTTP 429 (kuota habis), aplikasi segera membatalkan request tanpa mencoba lagi.
- **Mengapa digunakan di project ini?**
  Mengulang request saat kuota API eksternal sudah habis adalah kesia-siaan yang hanya memperlambat respon ke pengguna dan berisiko terkena penalti blokir IP.
- **Masalah apa yang diselesaikan?**
  Meningkatkan keandalan sistem terhadap gangguan jaringan sementara dan melindungi kuota akun.
- **Apa trade-off-nya?**
  Pengguna menunggu sedikit lebih lama saat terjadi *retry* sebelum menerima pesan error.
- **Di mana kodenya dapat dipelajari?**
  - [aviationstack.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/clients/aviation/aviationstack.py)

---

### 14. In-Memory Telemetry & Operational Metrics
- **Apa itu?**
  Pencatatan metrik operasional aplikasi (jumlah request ke Aviationstack, jumlah error, hitungan HTTP 429, latensi p95, rasio cache hit/miss) langsung di memori proses secara ringan.
- **Mengapa digunakan di project ini?**
  Memungkinkan developer dan tim DevOps memantau kesehatan integrasi eksternal secara instan melalui endpoint `/api/v1/health` tanpa perlu memasang sistem monitoring eksternal yang berat untuk portfolio.
- **Masalah apa yang diselesaikan?**
  Memberikan visibilitas langsung terhadap status kuota Aviationstack dan efektivitas cache.
- **Apa trade-off-nya?**
  Metrik di-reset jika proses aplikasi di-restart.
- **Di mana kodenya dapat dipelajari?**
  - [metrics.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/core/metrics.py)
  - [health.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/api/v1/routes/health.py)

---

### 15. Boundary Defense: Raw Schema vs Domain DTO vs API Response
- **Apa itu?**
  Pemisahan ketat model data di perbatasan sistem:
  1. *Raw Schema*: Memvalidasi struktur respon kotor dari API Aviationstack.
  2. *Domain DTO*: Entitas internal bersih yang digunakan dalam logika bisnis aplikasi.
  3. *API Response*: Struktur data yang diekspos ke klien frontend.
- **Mengapa digunakan di project ini?**
  Jika Aviationstack mengubah nama field atau format JSON-nya di masa mendatang, perubahan hanya perlu ditangani di lapisan *Raw Schema* dan *Mapper*, tanpa merusak database ataupun frontend kita.
- **Masalah apa yang diselesaikan?**
  Menghilangkan ketergantungan rapuh (*brittle coupling*) pada format eksternal.
- **Apa trade-off-nya?**
  Membutuhkan lebih banyak file deklarasi model (schemas, dto, mapper).
- **Di mana kodenya dapat dipelajari?**
  - [schemas.py (Raw)](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/clients/aviation/schemas.py)
  - [base.py (DTO)](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/clients/aviation/base.py)
  - [mapper.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/clients/aviation/mapper.py)
  - [flight.py (API Schemas)](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/schemas/flight.py)

---

### 16. Modular Monolith Architecture
- **Apa itu?**
  Aplikasi monolitik tunggal yang secara internal dibagi menjadi modul-modul fungsional yang independen dan memiliki batas tanggung jawab (*clear domain boundaries*).
- **Mengapa digunakan di project ini?**
  Memberikan kemudahan *deploy*, *debug*, dan *test* seperti monolit, tetapi mempertahankan kerapian kode seperti microservices.
- **Masalah apa yang diselesaikan?**
  Menghindari *premature optimization* dan kerumitan operasional microservices (seperti deployment 10 container berbeda atau kegagalan jaringan internal).
- **Apa trade-off-nya?**
  Disiplin tim diperlukan agar tidak terjadi *cross-boundary imports* yang merusak isolasi domain.
- **Di mana kodenya dapat dipelajari?**
  - [001-modular-monolith.md](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/docs/adr/001-modular-monolith.md)
  - [architecture.md](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/docs/architecture.md)

---

### 17. Docker Multi-Stage Build & Non-Root Containers
- **Apa itu?**
  Teknik pembuatan container di mana compiler, devDependencies, dan file sementara dibuang pada tahap perantara, menyisakan hanya runtime dan binary esensial di image akhir, yang dijalankan dengan user biasa (*non-root*).
- **Mengapa digunakan di project ini?**
  Memperkecil ukuran Docker image dari ~1.2GB menjadi ~150MB dan mencegah penyerang menguasai server host jika terjadi celah keamanan di dalam container.
- **Masalah apa yang diselesaikan?**
  Waktu download/deploy lambat dan risiko keamanan tingkat tinggi (*container breakout*).
- **Apa trade-off-nya?**
  File `Dockerfile` menjadi sedikit lebih panjang karena memuat beberapa tahap (`FROM ... AS ...`).
- **Di mana kodenya dapat dipelajari?**
  - [backend/Dockerfile](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/Dockerfile)
  - [frontend/Dockerfile](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/frontend/Dockerfile)

---

### 18. Zero-Disk Redis Volume Architecture
- **Apa itu?**
  Mengonfigurasi Redis dengan opsi `--save "" --appendonly no` dan tidak menghubungkannya ke volume disk pada `docker-compose.yml`.
- **Mengapa digunakan di project ini?**
  Redis murni digunakan sebagai cache sementara. Seluruh data permanen telah tersimpan aman di PostgreSQL.
- **Masalah apa yang diselesaikan?**
  Menghilangkan beban baca/tulis disk I/O yang tidak perlu pada server hosting dan mencegah disk penuh akibat snapshot cache usang.
- **Apa trade-off-nya?**
  Data cache akan kosong setelah restart container Redis, namun aplikasi akan secara otomatis mengisi ulang cache dari database atau provider.
- **Di mana kodenya dapat dipelajari?**
  - [docker-compose.yml](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/docker-compose.yml)

---

### 19. Alembic Declarative Database Versioning
- **Apa itu?**
  Sistem pelacakan dan versioning skema database secara terstruktur menggunakan script Python berbasis deklarasi model SQLAlchemy.
- **Mengapa digunakan di project ini?**
  Memastikan bahwa perubahan struktur tabel (penambahan kolom, indeks, relasi baru) dapat diterapkan secara otomatis dan deterministik di lingkungan development, CI/CD, maupun production.
- **Masalah apa yang diselesaikan?**
  Menghilangkan manipulasi tabel manual langsung di database yang rentan kesalahan manusia (*human error*) dan inkonsistensi antar lingkungan.
- **Apa trade-off-nya?**
  Setiap perubahan model harus diiringi pembuatan file migrasi baru.
- **Di mana kodenya dapat dipelajari?**
  - [alembic.ini](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/alembic.ini)
  - [versions/20260918_0001_initial_schema.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/alembic/versions/20260918_0001_initial_schema.py)

---

### 20. Next.js 15 App Router & Server/Client Components
- **Apa itu?**
  Arsitektur modern React di mana komponen secara default di-render di server (*Server Components*), dan hanya komponen yang membutuhkan interaktivitas pengguna (state, event handler) yang dideklarasikan sebagai *Client Components* (`"use client"`).
- **Mengapa digunakan di project ini?**
  Mengurangi ukuran bundle JavaScript yang dikirim ke browser secara drastis dan mempercepat waktu *First Contentful Paint* (FCP).
- **Masalah apa yang diselesaikan?**
  Aplikasi web tradisional React sering kali lambat dimuat pertama kali karena browser harus mengunduh dan mengeksekusi megabyte JavaScript sebelum menampilkan antarmuka.
- **Apa trade-off-nya?**
  Developer harus memahami batasan apa saja yang boleh dan tidak boleh dilakukan di Server Components (misalnya: tidak boleh menggunakan `useState` di Server Component).
- **Di mana kodenya dapat dipelajari?**
  - [layout.tsx](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/frontend/app/layout.tsx)
  - [page.tsx (Home)](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/frontend/app/page.tsx)
  - [dashboard/page.tsx](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/frontend/app/dashboard/page.tsx)

---

### 21. TanStack React Query: Stale-While-Revalidate
- **Apa itu?**
  Pustaka pengelola status asinkron untuk frontend yang otomatis meng-cache respon HTTP, menyajikan data yang ada secara instan (*stale*), lalu melakukan sinkronisasi di latar belakang (*revalidate*).
- **Mengapa digunakan di project ini?**
  Mencegah *duplicate network requests* saat pengguna berpindah-pindah halaman, dan memberikan pengalaman pengguna yang sangat cepat tanpa layar loading kosong berulang kali.
- **Masalah apa yang diselesaikan?**
  Menghilangkan kode boilerplate `useEffect` dan `useState` yang rumit dan rawan *race conditions*.
- **Apa trade-off-nya?**
  Menambah sedikit ukuran dependensi frontend (~12kB gzipped).
- **Di mana kodenya dapat dipelajari?**
  - [query-provider.tsx](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/frontend/lib/query-provider.tsx)
  - [flights/page.tsx](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/frontend/app/flights/page.tsx)

---

### 22. Dark Mode & Design Tokens dengan Tailwind CSS
- **Apa itu?**
  Sistem desain berbasis utilitas CSS modern dengan palet warna terkurasi (Slate, Zinc, Cyan, Amber, Rose) yang dirancang khusus bernuansa kokpit avionik malam hari.
- **Mengapa digunakan di project ini?**
  Memberikan identitas visual yang profesional, futuristik, dan nyaman di mata untuk pemantauan radar penerbangan dalam jangka waktu lama.
- **Masalah apa yang diselesaikan?**
  Mencegah tampilan antarmuka generik yang membosankan dan memastikan konsistensi visual di seluruh komponen aplikasi.
- **Apa trade-off-nya?**
  Nama kelas Tailwind bisa terlihat panjang pada elemen JSX, namun sangat mudah dimodifikasi tanpa efek samping ke elemen lain (*scoped styling*).
- **Di mana kodenya dapat dipelajari?**
  - [globals.css](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/frontend/app/globals.css)
  - [tailwind.config.js](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/frontend/tailwind.config.js)

---

### 23. Zero-SQLite Compromise: Real PostgreSQL in Tests
- **Apa itu?**
  Keputusan arsitektur untuk menjalankan pengujian integrasi database menggunakan PostgreSQL sungguhan, bukan SQLite in-memory.
- **Mengapa digunakan di project ini?**
  SQLite memiliki dialek SQL, penanganan tipe data (seperti UUID dan JSONB), serta konkurensi kunci yang sangat berbeda dari PostgreSQL.
- **Masalah apa yang diselesaikan?**
  Mencegah fenomena *"Works in SQLite tests, fails in PostgreSQL production"* akibat perbedaan fitur seperti `ON CONFLICT DO UPDATE` atau fungsi JSONB.
- **Apa trade-off-nya?**
  Memerlukan container PostgreSQL yang menyala saat menjalankan test integrasi lokal atau pipeline CI.
- **Di mana kodenya dapat dipelajari?**
  - [003-postgresql-for-integration-tests.md](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/docs/adr/003-postgresql-for-integration-tests.md)
  - [ci.yml](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/.github/workflows/ci.yml)

---

### 24. Mitigasi IDOR (Insecure Direct Object Reference)
- **Apa itu?**
  Pencegahan kerentanan keamanan di mana pengguna dapat mengakses, mengubah, atau menghapus objek milik pengguna lain hanya dengan menebak ID objek tersebut pada parameter URL.
- **Mengapa digunakan di project ini?**
  Data favorit dan riwayat pencarian bersifat pribadi bagi setiap pengguna terdaftar.
- **Masalah apa yang diselesaikan?**
  Setiap operasi SQL selalu menyertakan klausa kepemilikan eksplisit:
  `DELETE FROM favorites WHERE id = :favorite_id AND user_id = :current_user_id`.
  Jika ID cocok tetapi bukan milik user yang sedang login, operasi otomatis mengembalikan 0 baris terpengaruh / 404 Not Found.
- **Apa trade-off-nya?**
  Developer harus disiplin menyertakan parameter `user_id` di setiap kueri repository.
- **Di mana kodenya dapat dipelajari?**
  - [favorite_repository.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/repositories/favorite_repository.py)
  - [search_history_repository.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/repositories/search_history_repository.py)

---

### 25. Analitik Jujur: 'Tracked Flights' vs 'Global Aviation'
- **Apa itu?**
  Keputusan penamaan dan pelabelan metrik yang jujur dan akurat secara ilmiah dalam antarmuka statistik dan laporan analitik.
- **Mengapa digunakan di project ini?**
  Sistem ini memantau sampel data penerbangan yang dicari dan diobservasi oleh pengguna, bukan seluruh penerbangan di muka bumi secara absolut.
- **Masalah apa yang diselesaikan?**
  Mencegah klaim statistik yang menyesatkan. Label yang digunakan adalah:
  - *Tracked Flights by Airline* (bukan "Total Maskapai Dunia")
  - *Observed On-Time Rate* (bukan "Akurasi Global Maskapai")
  - *Observed Delay Rate* (bukan "Keterlambatan Bandara Global")
  - *Top Tracked Departure/Arrival Hubs*
- **Apa trade-off-nya?**
  Metrik merefleksikan volume data yang tersimpan di sistem, yang diiringi catatan transparansi metodologi di halaman dashboard.
- **Di mana kodenya dapat dipelajari?**
  - [analytics_service.py](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/backend/app/services/analytics_service.py)
  - [dashboard/page.tsx](file:///d:/Tugas%20Kuleah/porto/project-porto/Ava/frontend/app/dashboard/page.tsx)
