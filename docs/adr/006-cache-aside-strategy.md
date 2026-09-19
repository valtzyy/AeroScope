# ADR 006: Strategi Pola Caching Cache-Aside dan Dynamic TTL

## Status
Diterima (Accepted)

## Konteks (Context)
Aviationstack API menerapkan batasan kuota permintaan (100 request/bulan pada free tier). Sementara itu, pengguna aplikasi penerbangan sering melakukan pencarian berulang untuk rute yang sama. Diperlukan strategi caching yang efektif untuk menyeimbangkan antara kesegaran data (*freshness*) dan penghematan kuota API.

## Keputusan (Decision)
Kami menerapkan pola **Cache-Aside** (*Lazy Loading*) dengan **Dynamic TTL (Time-To-Live)** dan **Normalisasi Cache Key**:

1. **Alur Cache-Aside**:
   - Aplikasi memeriksa cache Redis menggunakan SHA-256 hash parameter query yang telah dinormalisasi.
   - Jika data ditemukan (*Cache Hit*), data langsung dikembalikan ke pengguna (< 10 ms).
   - Jika data tidak ada (*Cache Miss*), aplikasi memanggil provider, menyimpan hasilnya ke database dan Redis, lalu mengembalikannya ke pengguna.
2. **Dynamic TTL Berdasarkan Kedinamisan Status Penerbangan**:
   - `active`: **3 menit (180 detik)** — posisi koordinat, kecepatan, dan ketinggian pesawat berubah cepat.
   - `scheduled`: **15 menit (900 detik)** — jadwal relatif stabil hingga mendekati waktu keberangkatan.
   - `landed` / `cancelled`: **120 menit (7200 detik)** — status penerbangan sudah final dan tidak akan berubah lagi.
   - Default: **5 menit (300 detik)**.
3. **Normalisasi Parameter Key**:
   - Parameter query di-trim, diubah ke huruf kecil/besar seragam, dan diurutkan sebelum di-hash, sehingga pencarian `SFO -> JFK` dan `sfo -> jfk` menghasilkan cache key yang identik.

## Alasan (Reason)
- Mencegah pemborosan kuota API Aviationstack pada pencarian yang sama oleh banyak pengguna.
- Menghindari *Cache Key Fragmentation* akibat variasi penulisan input pengguna.
- Menghargai sifat data: data penerbangan yang sudah mendarat tidak perlu diperbarui sesering pesawat yang sedang di udara.

## Konsekuensi & Trade-off (Consequences)
- **Trade-off**: Data pada status *active* bisa memiliki jeda kesegaran hingga 3 menit.
- **Mitigasi**: UI secara transparan menampilkan label "Last synchronized: [Timestamp]" dan menyediakan tombol manual "Refresh Flight Status" yang dibatasi oleh rate limiter.
