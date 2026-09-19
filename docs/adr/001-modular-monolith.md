# ADR 001: Penggunaan Arsitektur Modular Monolith

## Status
Diterima (Accepted)

## Konteks (Context)
Sistem *Aviation Monitoring & Analytics Platform* memerlukan arsitektur yang tangguh, mudah dipelihara, dan dapat diuji secara menyeluruh. Terdapat pilihan untuk memecah sistem menjadi microservices terdistribusi (misal: Auth Service terpisah, Flight Service terpisah, Analytics Service terpisah) atau membangunnya sebagai monolith modular.

## Keputusan (Decision)
Kami memutuskan untuk menggunakan arsitektur **Modular Monolith** menggunakan **FastAPI** di backend dan **Next.js** di frontend.

Modul-modul domain (Auth, Flights, Favorites, Search History, Analytics) diorganisir dalam paket-paket terpisah dengan batasan tanggung jawab yang jelas (*Separation of Concerns*), namun tetap berjalan dalam satu proses aplikasi dan terhubung ke satu basis data utama.

## Alasan (Reason)
1. **Mengurangi Kompleksitas Operasional**: Microservices membutuhkan service mesh, message broker, distributed tracing, dan deployment terpisah yang berlebihan (*over-engineering*) untuk skala sistem ini.
2. **Integritas Data Transaksional**: Relasi antar data (misalnya pengguna dengan favorit dan riwayat pencarian) dapat dikelola dengan foreign key dan transaksi ACID PostgreSQL secara langsung.
3. **Efisiensi Pengembangan & Pembelajaran**: Mempermudah pengembang junior/intermediate untuk memahami aliran data dari ujung ke ujung tanpa harus berurusan dengan latensi jaringan antar layanan mikro.
4. **Siap Dipisahkan di Masa Depan**: Karena batasan antar modul dirancang bersih melalui service layer dan interface provider, modul tertentu dapat dipisah menjadi microservice secara mudah jika kebutuhan traffic di masa depan menghendakinya.

## Konsekuensi & Trade-off (Consequences)
- **Trade-off**: Seluruh modul backend berbagi runtime dan database yang sama. Bug kritis yang menyebabkan memori bocor dapat mempengaruhi modul lain.
- **Mitigasi**: Menerapkan automated unit & integration test yang ketat, isolasi exception handling, dan rate limiting per endpoint.

## Alternatif yang Dipertimbangkan (Alternatives Considered)
- **Microservices Architecture**: Ditolak karena memperkenalkan *network overhead*, kerumitan orkestrasi Kubernetes, dan biaya infrastruktur yang tidak perlu untuk portofolio ini.
- **Monolith Tradisional Tanpa Modul**: Ditolak karena rentan menghasilkan *spaghetti code* di mana query database bercampur dengan business logic dan route handler.
