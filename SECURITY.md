# Kebijakan Keamanan (Security Policy) — Aviation Monitoring & Analytics Platform

Dokumen ini menjelaskan postur keamanan, penanganan rahasia, serta prosedur pelaporan kerentanan untuk sistem **Aviation Monitoring & Analytics Platform**.

---

## 1. Prinsip Keamanan Inti (Core Security Principles)

1. **Defense in Depth**: Keamanan diterapkan berlapis mulai dari network (CORS), transport (HTTPS & HttpOnly cookies), aplikasi (Pydantic validation, sanitasi, rate limiting), hingga database (parameterized queries).
2. **Prinsip Hak Akses Terendah (Least Privilege)**: Database user hanya memiliki hak akses yang dibutuhkan oleh aplikasi (bukan superuser PostgreSQL).
3. **Isolasi Rahasia Penuh**: Kunci eksternal (`AVIATIONSTACK_API_KEY`) hanya disimpan dan dibaca di sisi server (backend environment). Frontend tidak pernah memiliki akses atau referensi terhadap kunci ini.
4. **Validasi Tanpa Kepercayaan (Never Trust Client Input)**: Semua data yang masuk divalidasi ketat di sisi backend menggunakan Pydantic v2.

---

## 2. Manajemen Kredensial & Secrets

- **Penyimpanan**: Kredensial disimpan via environment variables yang dibaca menggunakan `pydantic-settings`.
- **Git Hygiene**: File `.env` masuk ke dalam `.gitignore`. Hanya file template `.env.example` yang boleh di-commit dengan nilai dummy.
- **Log Masking**: Format log terstruktur menyamarkan API key (`av_***`), password, dan authorization header untuk mencegah kebocoran rahasia ke agregator log.

---

## 3. Otentikasi & Otorisasi

- **Password Hashing**: Menggunakan algoritma **Argon2id** yang tahan terhadap serangan GPU cracking, brute-force, dan side-channel attack. Password plaintext tidak pernah disimpan atau dicatat dalam log.
- **Token Transport**: JSON Web Token (JWT) dikirimkan melalui cookie HTTP dengan flag:
  - `HttpOnly`: Mencegah script JavaScript pihak ketiga / celah XSS membaca token otentikasi.
  - `SameSite=Lax`: Mencegah pengiriman cookie otomatis pada serangan Cross-Site Request Forgery (CSRF).
  - `Secure`: Menginstruksikan browser agar cookie hanya dikirim melalui koneksi terenkripsi HTTPS (diaktifkan di lingkungan produksi).
- **Backend Authorization**: Hak akses diperiksa secara ketat di backend melalui dependency injection FastAPI (`require_admin`, ownership validation). Aplikasi tidak mengandalkan status UI di frontend untuk menentukan hak akses data.

---

## 4. Proteksi Quota & Upstream Rate Limiting

- **Cache-Aside Layer**: Seluruh pencarian penerbangan disimpan sementara di Redis dengan TTL dinamis untuk meminimalkan beban request ke Aviationstack API.
- **Rate Limiting Internal**: Endpoint autentikasi dan pencarian dibatasi menggunakan algoritma token bucket untuk mencegah abuse dan serangan DoS.
- **Circuit Breaker / Bounded Backoff**: Request ke Aviationstack hanya di-retry pada kegagalan transient network (502/503/timeout). Respon status `429 Too Many Requests` langsung dihentikan tanpa retry untuk mencegah pemblokiran IP oleh provider.

---

## 5. Prosedur Pelaporan Kerentanan (Reporting a Vulnerability)

Jika Anda menemukan kerentanan keamanan potensial di repositori ini:
1. **JANGAN** membuat issue publik di GitHub.
2. Kirimkan laporan detail mencakup:
   - Deskripsi kerentanan dan potensi dampaknya.
   - Langkah-langkah reproduksi atau proof-of-concept (PoC).
   - Usulan perbaikan (jika ada).
3. Tim pengembang akan merespons dalam waktu 48 jam dan memprioritaskan patching sesuai tingkat keparahan CVSS.
