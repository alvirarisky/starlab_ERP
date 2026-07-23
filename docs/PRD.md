# PRD — Modul Quotation & Master Data

## ERP PT Starlab Analitik Indonesia (SAI) — Frappe/ERPNext

**Status:** Draft v1 — PRD utama/fondasi untuk Rilis 1 (Must-have)
**Basis dokumen:** BRA ERP SAI, Project Plan ERP SAI
**Modul terkait berikutnya:** Work Order Pengujian (PRD terpisah, dependency dari modul ini)

> **Catatan untuk AI Agent:** PRD ini adalah dokumen acuan utama implementasi modul Quotation & Master Data pada proyek ERP PT Starlab Analitik Indonesia (SAI) berbasis Frappe Framework/ERPNext. Dokumen sumber tambahan (BRA, TSD, Project Plan ERP SAI) ada di folder `/docs/` pada root project ini — baca dokumen tersebut untuk konteks lebih lengkap bila diperlukan. Ikuti instruksi berikut saat men-generate atau mengubah kode berdasarkan PRD ini:
>
> 1. Nama teknis DocType, field, dan API tetap dalam Bahasa Inggris; label yang tampil ke user (label field, judul menu, pesan) dalam Bahasa Indonesia — lihat Bagian 5.6.
> 2. Jangan mengubah urutan approval (Bagian 5.3) atau logika revisi di luar yang sudah didefinisikan tanpa konfirmasi eksplisit dari Product Owner — masih berstatus asumsi kerja (lihat poin berikutnya & Bagian 9).
> 3. Setiap item di Bagian 9 (Open Questions) masih terbuka — jangan diam-diam mengambil keputusan sendiri saat implementasi; beri tanda `// TODO: lihat PRD Bagian 9` di kode terkait, atau tanyakan balik ke user.
> 4. Dokumen ini adalah PRD fondasi/utama — modul lanjutan (Work Order Pengujian, Sample Tracking, dst.) akan punya PRD terpisah yang mereferensikan modul ini; jangan menggabungkan requirement modul lain ke sini.
>
> Beberapa keputusan approval di dokumen ini adalah **asumsi kerja** mengikuti rekomendasi BRA, karena Fase 0 (resolusi konflik BRA Bagian 8 + sign-off Direksi, per Project Plan) belum selesai.

---

## 1. Overview / Problem Statement

SAI saat ini menjalankan proses quotation ("surat penawaran") secara manual: disusun per proyek di Excel, dikirim/dikomunikasikan lewat WhatsApp dan email, dan disetujui secara verbal/berjenjang tanpa jejak digital. Berdasarkan BRA:

- **"Bikin penawaran" adalah bottleneck tertinggi Administrasi** — tabel rincian parameter, regulasi acuan, frekuensi, qty per titik, dan harga satuan disusun manual per proyek.
- **"Revisi berulang"** adalah pain point utama yang disebut Administrasi.
- **Approval quotation adalah proses approval paling kompleks** di antara seluruh dokumen SAI — melibatkan 5 approver (MT, MM, Finance, Marketing, Direksi) tanpa urutan atau jejak digital yang jelas.
- Tidak ada satu sumber data tunggal untuk data referensi (klien, parameter uji, regulasi acuan, harga) — semua diketik ulang manual tiap kali membuat quotation baru.

Modul ini membangun fondasi Master Data (Klien, Parameter Uji, Regulasi Acuan, Price List) sekaligus mendigitalisasi siklus hidup Quotation dari pembuatan sampai trigger otomatis ke Work Order, dengan approval berjenjang yang terlacak dan bereskalasi otomatis.

---

## 2. Goals & Non-Goals

### Goals

1. Menyediakan satu sumber data tunggal untuk Master Data yang dipakai berulang: Klien, Parameter Uji & Regulasi Acuan, Price List referensi.
2. Mendigitalisasi pembuatan Quotation lengkap dengan tabel parameter (matriks, regulasi, frekuensi, qty, harga) mengikuti format surat penawaran SAI yang sudah ada.
3. Mengurangi waktu pembuatan quotation dan jumlah siklus revisi dibanding proses manual saat ini.
4. Menyediakan approval berjenjang digital (MT → MM → Finance → Marketing → Direksi) yang terlacak, dengan status real-time dan eskalasi otomatis (SLA 1x24 jam).
5. Mendukung harga yang dapat dinegosiasikan per transaksi (bukan harga tetap per klien), dengan Price List sebagai referensi default.
6. Memicu pembuatan Work Order secara otomatis begitu Direksi memberi approval akhir.
7. Menjadikan dokumen ini sebagai PRD utama/fondasi — perubahan/penambahan modul berikutnya dibuatkan PRD terpisah, bukan mengedit dokumen ini.

### Non-Goals (untuk rilis ini)

- **Tidak ada Client Portal** atau antarmuka approval digital untuk klien — interaksi klien tetap offline (PDF/email/WA).
- **Tidak mencakup alur quotation untuk parameter Subkontraktor** (status "Subkon" di BRA Bagian 8 Poin 5) — ditandai Out of Scope, menunggu klarifikasi F0-5.
- **Tidak mencakup proses CRM/akuisisi klien sebelum tahap quotation** (leads, negosiasi awal) — belum ada input dari Marketing (F0-6 belum selesai).
- **Tidak ada mesin perhitungan pajak otomatis/integrasi sistem pajak eksternal** — PPN hanya berupa field terstruktur yang diisi manual.
- **Bukan keputusan approval final** — urutan approval di dokumen ini adalah asumsi kerja berbasis BRA, menunggu sign-off resmi Direksi di Fase 0.

---

## 3. Target Users

| Role                            | Kebutuhan Utama di Modul Ini                                                                                                     |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Administrasi** (primary user) | Membuat, merevisi, submit quotation; memantau status approval; input status client (approved/rejected/PO diterima) secara manual |
| **Manajer Teknis (MT)**         | Approve/reject quotation dari sisi kelayakan teknis (approver pertama)                                                           |
| **Manajer Mutu (MM)**           | Approve/reject dari sisi kepatuhan mutu                                                                                          |
| **Finance**                     | Approve/reject dari sisi kelayakan finansial/harga                                                                               |
| **Marketing**                   | Approve/reject dari sisi hubungan klien/komersial (approver wajib sesuai BRA; peran persisnya menunggu validasi F0-6)            |
| **Direksi**                     | Approver akhir; sign-off final quotation, memicu pembuatan Work Order                                                            |
| **Client** (eksternal, offline) | Menerima quotation via PDF/email/WA; memberi persetujuan/PO secara offline — bukan pengguna sistem di rilis ini                  |

---

## 4. User Stories

### Administrasi

- Sebagai Administrasi, saya ingin membuat Quotation baru dengan merujuk Master Data (Klien, Parameter Uji, Regulasi Acuan, Price List) agar tidak perlu mengetik ulang data referensi setiap kali.
- Sebagai Administrasi, saya ingin menambahkan banyak baris parameter uji (matriks, regulasi acuan, frekuensi, qty per titik, harga satuan) ke satu quotation agar sesuai format surat penawaran SAI yang sudah berjalan.
- Sebagai Administrasi, saya ingin mengubah harga satuan per baris dari harga referensi Price List (negosiasi) tanpa perlu approval tambahan di luar alur approval standar.
- Sebagai Administrasi, saya ingin mengisi PPN dan syarat pembayaran (DP/termin) sebagai field terstruktur di quotation, bukan teks bebas.
- Sebagai Administrasi, saya ingin men-submit quotation untuk approval dan melihat status real-time (sedang di approver mana) agar tidak perlu menanyakan status lewat WA.
- Sebagai Administrasi, ketika quotation di-reject, saya ingin melihat alasan reject dan merevisi quotation, dengan approval yang sudah didapat sebelumnya tetap tersimpan (tidak perlu mengulang dari awal).
- Sebagai Administrasi, saya ingin Work Order otomatis terbuat begitu Direksi memberi approval akhir, tanpa langkah konversi manual tambahan.
- Sebagai Administrasi, saya ingin quotation otomatis kedaluwarsa 30 hari sejak terbit jika klien belum merespons, agar tidak ada quotation menggantung tanpa batas waktu.

### Approver (MT, MM, Finance, Marketing, Direksi)

- Sebagai approver, saya ingin menerima notifikasi saat sebuah quotation menunggu approval saya, agar tidak perlu diberi tahu manual lewat WA.
- Sebagai approver, saya ingin menerima notifikasi eskalasi jika saya belum bertindak dalam 1x24 jam, agar approval tidak diam tanpa tindak lanjut.
- Sebagai approver, saya ingin bisa approve atau reject dengan wajib mengisi alasan saat reject, agar Administrasi tahu apa yang perlu diperbaiki.

### Direksi

- Sebagai Direksi, saya ingin melihat status lengkap rantai approval sebuah quotation (siapa sudah approve, siapa masih pending) sebelum memberi approval akhir.

---

## 5. Functional Requirements

### 5.1 Master Data (prasyarat)

- **Customer/Klien** — perluasan DocType `Customer` ERPNext dengan field tambahan (jenis industri, PIC) sesuai rekomendasi BRA.
- **Test Parameter** (Custom DocType) — parameter uji, matriks pengujian (Udara Ambien/Udara Lingkungan Kerja/Emisi/Air Permukaan/Air Bersih/Air Limbah/Tanah/Sedimen), regulasi acuan (SNI/Permenkes/PP), satuan, metode uji.
- **Price List** — harga satuan referensi/default per Test Parameter, dipakai sebagai default yang bisa diubah manual saat pembuatan quotation (bukan harga mengikat per klien).

### 5.2 Quotation — Struktur Data

- Perluasan `Quotation` (Selling) ERPNext dengan **custom child table** baris parameter: Parameter Uji, Matriks, Regulasi Acuan, Frekuensi, Qty per Titik, Harga Satuan (default dari Price List, editable), Harga Total (kalkulasi otomatis).
- **Auto-numbering** mengikuti format yang sudah dipakai SAI (contoh dari BRA: `Quo-SAI/V/2026/076` — bulan romawi/tahun/nomor urut). _Format persis perlu dikonfirmasi ke Administrasi saat technical design (lihat Open Questions)._
- Field terstruktur: **PPN (%)**, **syarat pembayaran** (DP %, termin pembayaran).
- Field **tanggal terbit** dan **tanggal kedaluwarsa** (otomatis = tanggal terbit + 30 hari).
- Field status siklus hidup: `Draft` → `Submitted` → `MT Review` → `MM Review` → `Finance Review` → `Marketing Review` → `Direksi Review` → `Approved` / `Perlu Revisi` → (jika Approved) `Converted to Work Order`.

### 5.3 Revisi & Approval Workflow

- Approval berjenjang via Frappe Workflow Builder, urutan: **MT → MM → Finance → Marketing → Direksi** (asumsi kerja per BRA, tunduk pada sign-off Fase 0 F0-1).
- Setiap step: aksi **Approve** atau **Reject**.
- **Reject**: quotation kembali ke status `Perlu Revisi` di tangan Administrasi, dengan **field alasan reject wajib diisi** oleh approver yang reject.
- **Revisi setelah reject atau setelah sebagian approval**: approval yang sudah didapat pada step-step sebelumnya **tetap valid** — workflow lanjut dari titik yang belum di-approve, tidak mengulang seluruh rantai dari awal. _(Aturan teknis persis siapa yang perlu di-notify ulang saat revisi — lihat Open Questions.)_
- **Approve final (Direksi)**: memicu pembuatan **Work Order Pengujian** secara otomatis oleh sistem (tanpa aksi manual konversi tambahan).

### 5.4 Notifikasi & Eskalasi SLA

- Notifikasi ke approver terkait saat quotation sampai di step approval-nya.
- **Eskalasi otomatis** jika approver tidak bertindak dalam **1x24 jam** _(target eskalasi ke siapa — lihat Open Questions)_.
- Notifikasi ke Administrasi setiap ada aksi Approve/Reject, dan saat quotation kedaluwarsa.

### 5.5 Interaksi dengan Client (Offline)

- Tidak ada Client Portal atau aksi client di sistem pada rilis ini.
- Sistem menyediakan **Print Format** (cetak/export PDF) quotation untuk dibagikan manual via email/WA.
- Administrasi meng-update status quotation secara manual berdasarkan respons client yang diterima offline (approved/rejected/PO diterima).

### 5.6 Lokalisasi Bahasa (Non-Functional)

- Seluruh label UI yang tampil ke user (field label, judul menu, tombol, pesan notifikasi, Print Format) menggunakan **Bahasa Indonesia**.
- Nama teknis internal (nama DocType, nama field/fieldname, nama API endpoint, nama variabel di Server Script) tetap menggunakan **Bahasa Inggris**, mengikuti konvensi standar Frappe Framework.
- Aktifkan fitur **Translation** bawaan Frappe agar sistem mendukung dwibahasa (default Bahasa Indonesia, opsi beralih ke Bahasa Inggris) — teks Indonesia dikelola lewat mekanisme translation string standar Frappe, bukan hard-code di level kode, agar mudah dikelola/diperluas ke modul lain.

---

## 6. Success Metrics

_(Arah target berdasarkan pain point BRA — belum ada baseline terukur saat ini, sehingga dinyatakan sebagai arah perbaikan, bukan angka pasti)_

- **Waktu pembuatan quotation** (draft → submit approval pertama) menurun signifikan dibanding proses manual Excel saat ini.
- **Jumlah revisi rata-rata per quotation** menurun dibanding kondisi "revisi berulang" yang jadi pain point utama Administrasi.
- **Approval cycle time end-to-end** (submit → Direksi approve) terukur dan lebih cepat dari proses verbal/WA, dibantu eskalasi SLA 1x24 jam.
- **Tingkat adopsi selama masa transisi** — persentase quotation yang dibuat lewat sistem vs masih manual (relevan karena Project Plan merencanakan Quotation & Work Order berjalan paralel dengan proses manual di awal Rilis 1).
- **Insiden quotation kedaluwarsa tanpa tindak lanjut** menurun berkat expiry date otomatis + notifikasi.

---

## 7. Dependencies

- Setup environment Frappe/ERPNext & Chart of Account awal (Project Plan — bisa berjalan paralel, tidak bergantung pada resolusi Fase 0).
- **Fase 0 F0-1** (resolusi arah approval MT ↔ Administrasi, BRA Bagian 8 Poin 1) dan sign-off Direksi — urutan approval di PRD ini tetap asumsi kerja sampai ini selesai.
- **Fase 0 F0-6** (requirement gathering ke Direksi & Marketing) — peran Marketing sebagai approver wajib diasumsikan dari BRA, belum divalidasi langsung.
- Modul **Work Order Pengujian** (PRD terpisah) bergantung pada trigger "Approved" dari modul ini.

---

## 8. Out of Scope

- Client Portal / approval digital oleh klien.
- Alur quotation & vendor management untuk parameter Subkontraktor.
- Proses CRM/lead pipeline sebelum tahap quotation.
- Mesin perhitungan pajak otomatis / integrasi sistem pajak eksternal.
- Sign-off formal Direksi/Marketing atas urutan approval (menunggu Fase 0).
- Dukungan multi-currency (tidak disebutkan sebagai kebutuhan di BRA).
- Template/library quotation tersimpan (tidak diminta).

---

## 9. Open Questions

1. **Target eskalasi SLA**: Eskalasi setelah 1x24 jam ditujukan ke siapa — atasan approver terkait, langsung ke Direksi, atau sekadar reminder ulang ke approver yang sama?
2. **Logika teknis revisi vs approval**: Saat revisi mengubah field yang jadi concern approver tertentu (misal harga berubah setelah MM approve, padahal harga itu ranah Finance) — apakah approval MM tetap valid, atau perlu aturan "approval yang levelnya setelah field yang berubah" yang di-invalidate? Perlu didalami dengan Dev1 saat technical design.
3. **Urutan approval final**: MT → MM → Finance → Marketing → Direksi masih asumsi kerja BRA — wajib divalidasi ulang setelah Fase 0 F0-1 selesai dan disetujui Direksi.
4. **Peran Marketing**: Dimasukkan sebagai approver wajib sesuai BRA, tapi Marketing belum pernah memberi input langsung (F0-6 belum selesai) — kemungkinan berubah setelah sesi tersebut.
5. **Format auto-numbering**: Asumsi format `Quo-SAI/[bulan romawi]/[tahun]/[no urut]` berdasarkan satu contoh di BRA (`Quo-SAI/V/2026/076`) — perlu dikonfirmasi ke Administrasi apakah ini format resmi atau ada variasi lain.
6. **Perpanjangan quotation kedaluwarsa**: Jika quotation kedaluwarsa (30 hari) sebelum client merespons, apakah Administrasi butuh aksi "aktifkan ulang/extend", atau harus selalu membuat quotation baru dari nol?

---

_Dokumen ini disusun berdasarkan BRA ERP SAI dan Project Plan ERP SAI, melalui diskusi bertahap untuk menyepakati asumsi kerja pada area yang belum diputuskan formal oleh SAI. Ditujukan sebagai rujukan development modul Quotation & Master Data, termasuk sebagai input teknis untuk Claude Code._
