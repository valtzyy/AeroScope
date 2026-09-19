# ADR 005: Autentikasi Berbasis HttpOnly Cookie (Bukan LocalStorage)

## Status
Diterima (Accepted)

## Konteks (Context)
Dalam aplikasi Single-Page Application (SPA) seperti Next.js yang berkomunikasi dengan REST API FastAPI, terdapat perdebatan mengenai tempat penyimpanan access token (JWT):
1. Menyimpan token di `localStorage` atau `sessionStorage` browser.
2. Menyimpan token di dalam `HttpOnly Cookie` yang dikelola langsung oleh browser.

## Keputusan (Decision)
Kami memutuskan untuk menggunakan **HttpOnly Cookie (`access_token`)** dengan flag `SameSite=Lax` dan `Secure` (di production).

Frontend JavaScript dilarang menyimpan atau memiliki akses langsung ke string token mentah. Frontend memeriksa status login melalui panggilan ke endpoint `/api/v1/auth/me` dengan `credentials: 'include'`.

## Alasan (Reason)
1. **Perlindungan Terhadap Serangan XSS (Cross-Site Scripting)**:
   Jika aplikasi memiliki celah XSS (misalnya dari library pihak ketiga yang terinfeksi), script jahat tidak akan pernah bisa membaca isi token karena pembatasan ketat browser pada flag `HttpOnly`.
2. **Mitigasi CSRF Otomatis**:
   Atribut `SameSite=Lax` mencegah browser menyertakan cookie otentikasi saat situs pihak ketiga melakukan request state-modifying (POST/DELETE/PUT) lintas origin.
3. **Pengalaman Pengguna yang Mulus**:
   Browser secara otomatis menangani pengiriman dan penghapusan cookie saat kedaluwarsa atau saat endpoint `/logout` dipanggil.

## Konsekuensi & Trade-off (Consequences)
- **Trade-off**: Memerlukan konfigurasi CORS yang lebih ketat (`allow_credentials=True`, daftar origin eksplisit tanpa wildcard `*`).
- **Mitigasi**: Telah dikonfigurasi secara deklaratif di `app.core.config.Settings.CORS_ORIGINS`.
