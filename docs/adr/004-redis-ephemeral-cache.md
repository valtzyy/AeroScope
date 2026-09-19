# ADR 004: Redis sebagai Ephemeral In-Memory Cache (Tanpa Persistensi Disk)

## Status
Diterima (Accepted)

## Konteks (Context)
Aplikasi menggunakan Redis untuk menyimpan cache respon kueri penerbangan dan status rate limiting. Timbul pertanyaan apakah Redis perlu dikonfigurasi dengan persistensi disk permanen (RDB snapshotting dan AOF - Append Only File) dengan persistent volume storage di Docker.

## Keputusan (Decision)
Kami memutuskan bahwa **Redis dijalankan murni sebagai Ephemeral Cache di memori** (`save ""` dan `appendonly no`), tanpa volume storage persisten.

Data transaksional dan permanen aplikasi (Users, Flights, Flight Observations, Favorites, Search History) seluruhnya disimpan di **PostgreSQL 16**.

## Alasan (Reason)
1. **Karakteristik Data Cache**: Data di dalam cache adalah data turunan sementara (*disposable data*) yang diambil dari Aviationstack atau database.
2. **Perilaku Pemulihan yang Diharapkan**: Jika container Redis restart:
   ```text
   Redis restart -> Cache kosong -> Request baru miss -> Data diambil dari provider/DB -> Cache terisi kembali secara otomatis
   ```
3. **Menghemat I/O & Disk**: Mencegah overhead penulisan disk yang tidak perlu dan menghilangkan risiko volume disk bocor atau penuh karena file AOF lama.
4. **Mencegah Cache Basi Persisten**: Menghindari masalah di mana cache data penerbangan yang sudah usang terbawa melintasi proses deployment atau container restart.

## Konsekuensi & Trade-off (Consequences)
- **Trade-off**: Sesaat setelah Redis restart, beberapa request awal akan mengalami *cache miss* dan memanggil provider eksternal.
- **Mitigasi**: Pola *cache-aside* dan persistensi PostgreSQL memastikan sistem tetap stabil dan responsif saat cache sedang diisi ulang.
