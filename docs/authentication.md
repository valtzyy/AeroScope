# Arsitektur & Alur Keamanan Otentikasi

Dokumen ini menjelaskan implementasi otentikasi berbasis **JWT** dan **HttpOnly Cookie** pada sistem **Aviation Monitoring & Analytics Platform**.

---

## 1. Diagram Alur Otentikasi (Authentication Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Pengguna (Browser)
    participant Client as Next.js Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL Database

    Note over User,DB: 1. Proses Registrasi
    User->>Client: Input email, nama, password (min 8 karakter)
    Client->>API: POST /api/v1/auth/register
    API->>API: Validasi skema & hash password dengan Argon2id
    API->>DB: Simpan record User baru (email lowercased unik)
    API-->>Client: HTTP 201 Created (User data)

    Note over User,DB: 2. Proses Login
    User->>Client: Input email & password
    Client->>API: POST /api/v1/auth/login
    API->>DB: Query User berdasarkan email
    API->>API: Verifikasi hash Argon2id (constant-time)
    API->>API: Generate access_token JWT (masa berlaku 15 menit)
    API-->>Client: HTTP 200 OK + Set-Cookie: access_token (HttpOnly; SameSite=Lax)

    Note over User,DB: 3. Permintaan Terautentikasi
    Client->>API: GET /api/v1/auth/me (Browser otomatis sertakan cookie)
    API->>API: Validasi signature & masa kedaluwarsa JWT
    API->>DB: Verifikasi status user aktif di database
    API-->>Client: HTTP 200 OK (Data profil user)

    Note over User,DB: 4. Proses Logout
    User->>Client: Klik Logout
    Client->>API: POST /api/v1/auth/logout
    API-->>Client: HTTP 200 OK + Set-Cookie: access_token=; Max-Age=0 (Cookie dihapus)
```

---

## 2. Mengapa Memilih HttpOnly Cookies Dibanding localStorage?

| Aspek | localStorage | HttpOnly Cookie (Dipilih) |
|---|---|---|
| **Akses JavaScript** | Dapat dibaca oleh script JavaScript apa pun (`window.localStorage.getItem(...)`) | **TIDAK DAPAT dibaca oleh JavaScript** di browser |
| **Ketahanan XSS** | **Rentan**: Script XSS jahat dapat mencuri token dan mengirimkannya ke server penyerang | **Tahan XSS**: Penyerang tidak dapat mengekstrak token dari memori browser |
| **Pengiriman Token** | Harus dipasang manual di setiap request via header `Authorization` | **Otomatis dikirim oleh browser** pada setiap request ke domain yang sama |
| **Mitigasi CSRF** | Tidak rentan CSRF jika via header | Diminimalisir dengan flag `SameSite=Lax` dan verifikasi header origin |

---

## 3. Detail Konfigurasi Cookie

Setiap cookie sesi disetel dengan atribut berikut:
- **`HttpOnly=True`**: Menginstruksikan mesin browser agar cookie tidak dapat diakses melalui properti `document.cookie`.
- **`SameSite=Lax`**: Memastikan cookie hanya dikirimkan pada navigasi tingkat atas dan request yang berasal dari origin yang sama, menangkis serangan CSRF standar.
- **`Secure=True` (di Production)**: Memastikan cookie hanya ditransmisikan melalui kanal terenkripsi HTTPS.
- **`Max-Age=900` (15 menit)**: Sesi dibatasi berumur pendek untuk meminimalisir risiko penyalahgunaan.

---

## 4. Algoritma Hashing Password: Argon2id

Aplikasi tidak menggunakan algoritma usang seperti MD5, SHA-1, atau SHA-256 murni untuk password. Kami menggunakan **Argon2id**:
1. **Memory-Hard**: Membutuhkan alokasi memori acak, membuat peretasan paralel menggunakan GPU atau ASIC hardware menjadi sangat mahal dan lambat.
2. **Resisten Side-Channel**: Varian hybrid (*id*) memberikan proteksi optimal terhadap serangan cache-timing dan serangan berbasis data-dependent.
