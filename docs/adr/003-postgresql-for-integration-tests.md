# ADR 003: Penggunaan PostgreSQL untuk Integration Testing (Bukan SQLite)

## Status
Diterima (Accepted)

## Konteks (Context)
Dalam pengembangan aplikasi Python, pengembang sering kali tergoda menggunakan SQLite in-memory untuk pengujian integrasi karena prosesnya cepat dan tidak memerlukan daemon database. Namun, sistem ini menggunakan fitur-fitur spesifik PostgreSQL seperti tipe data `UUID`, kolom `JSONB` untuk parameter pencarian, locking concurrency, serta penanganan tipe data tanggal dan zona waktu UTC.

## Keputusan (Decision)
Kami memutuskan bahwa **seluruh Integration Tests WAJIB dijalankan di atas PostgreSQL 16 asli** (baik via Docker Compose di lokal maupun Service Container di GitHub Actions).

SQLite dilarang digunakan sebagai database pengganti pada integration test. Unit test tetap menggunakan mock/fake in-memory murni tanpa ketergantungan database.

## Alasan (Reason)
1. **Paritas Lingkungan (Environment Parity)**: Memastikan perilaku database saat testing 100% identik dengan lingkungan produksi. Menghilangkan sindrom *"berhasil di SQLite saat test, tetapi gagal/error syntax saat di-deploy ke PostgreSQL produksi"*.
2. **Dukungan Fitur PostgreSQL**: SQLite tidak mendukung tipe data `JSONB` secara native dengan operator query yang sama, tidak memiliki constraint perbandingan tipe yang ketat, dan memiliki penanganan datetime yang berbeda.
3. **Integritas Constraint & Index**: Menjamin index komposit `(flight_id, observed_at)` dan foreign key cascade benar-benar teruji di engine database yang sesungguhnya.

## Konsekuensi & Trade-off (Consequences)
- **Trade-off**: Menjalankan integration test di komputer lokal memerlukan instance PostgreSQL yang aktif (via Docker `docker compose up -d postgres`).
- **Mitigasi**: Kami menyediakan unit test murni yang sangat cepat (< 5 detik) untuk feedback loop instan saat koding tanpa memerlukan database berjalan. Integration test dijalankan sebelum commit/PR atau secara otomatis di CI pipeline.

## Alternatif yang Dipertimbangkan (Alternatives Considered)
- **SQLite In-Memory**: Ditolak karena menyamarkan bug kompatibilitas SQL dan tipe data.
