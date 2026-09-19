# ADR 002: Abstraksi Provider Data Penerbangan (FlightDataProvider Interface)

## Status
Diterima (Accepted)

## Konteks (Context)
Aplikasi membutuhkan data penerbangan terkini dari Aviationstack. Namun, jika kode business logic (service layer dan route handler) langsung melakukan HTTP request ke Aviationstack:
1. Domain aplikasi menjadi terikat ketat (*tightly coupled*) pada struktur JSON mentah pihak ketiga.
2. Pengujian otomatis (unit & integration tests) akan terpaksa memanggil API eksternal, yang menghabiskan kuota request bulanan dan membuat testing lambat serta fluktuatif jika koneksi internet terganggu.
3. Sulit untuk berpindah atau menambahkan provider cadangan (seperti FlightAware, OpenSky, atau mock offline) di masa depan.

## Keputusan (Decision)
Kami memutuskan untuk membuat antarmuka abstrak **`FlightDataProvider`** (menerapkan prinsip *Dependency Inversion* dari SOLID).

Implementasi konkret terdiri dari:
1. **`AviationstackProvider`**: Menghubungi API live Aviationstack melalui HTTPX dengan bounded exponential backoff retries dan pemetaan status error khusus.
2. **`MockFlightProvider`**: Menyajikan dataset fixture deterministik lokal untuk pengujian offline dan CI tanpa kuota.

Mode aktif dipilih secara eksplisit melalui environment variable:
`FLIGHT_PROVIDER=aviationstack` atau `FLIGHT_PROVIDER=mock`.

## Alasan (Reason)
- **Loose Coupling**: Business logic hanya mengenal DTO internal (`FlightDTO`, `ObservationDTO`). Format JSON upstream yang bersarang dipetakan secara terpusat di layer mapper.
- **Efisiensi Biaya & Quota**: Pengujian unit dan pengujian frontend dapat berjalan penuh dengan `MockFlightProvider` tanpa menghabiskan kuota API key.
- **Fail-Fast**: Jika mode `aviationstack` dipilih tanpa API key, sistem menolak booting dengan pesan error yang jelas, tanpa *silent fallback* yang membingungkan.

## Konsekuensi & Trade-off (Consequences)
- **Trade-off**: Memerlukan layer abstraksi dan mapper tambahan yang menambah sedikit jumlah baris kode (boilerplate).
- **Manfaat**: Peningkatan drastis pada aspek *testability*, *maintainability*, dan portabilitas sistem jangka panjang.
