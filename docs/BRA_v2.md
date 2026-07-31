# BUSINESS REQUIREMENT ANALYSIS (BRA)

## Pengembangan Sistem ERP — PT Starlab Analitik Indonesia

**Disusun oleh:** Senior ERP Business Analyst / Business Process Analyst / Frappe-ERPNext Solution Architect.

**Basis analisis:** 1 kuesioner requirement gathering (6 responden lintas divisi) + 7 dokumen internal (rekening koran, work order pengujian, daftar induk dokumen mutu, data QC pengujian, laporan kas operasional harian, rekap work order, surat penawaran).

## Daftar Isi

1. Executive Summary
2. Company Overview
3. Existing Business Process (As-Is) & Requirement per Divisi
4. Functional Requirements
5. Non-Functional Requirements
6. Business Process Mapping
7. Gap Analysis (As-Is vs To-Be)
8. Gap/Konflik Antar Dokumen — Perlu Klarifikasi
9. ERP Module Recommendation & Frappe/ERPNext Customization Mapping
10. Implementation Roadmap
11. Risks & Assumptions
12. Questions for Stakeholders
13. Final Recommendation
14. Addendum — Pembaruan Pasca-BRA

---

## 1. Executive Summary

PT Starlab Analitik Indonesia (SAI) adalah laboratorium pengujian lingkungan terakreditasi (mengacu ISO/IEC 17025 — terlihat dari struktur Panduan Mutu/Prosedur Operasional/Instruksi Kerja Metode di Daftar Induk Dokumen) yang berbasis di Bogor, Jawa Barat. Bisnis intinya adalah jasa pengujian kualitas lingkungan (udara ambien, udara emisi, air permukaan, air bersih/minum, air limbah, tanah, sedimen) untuk klien korporat dan institusi.

Hasil cross-analysis menunjukkan bahwa operasional SAI saat ini berjalan di atas kombinasi Excel, WhatsApp, Google Drive, dokumen kertas/form manual, dan sedikit "sistem internal" yang tidak terintegrasi. Tidak ada satu sumber data tunggal (single source of truth). Setiap divisi menyimpan salinan datanya sendiri, saling bertukar data lewat WhatsApp/Excel, dan proses persetujuan berjenjang berjalan tanpa jejak digital yang bisa dilacak.

Titik nyeri (pain points) yang paling sering muncul di 6 responden: data sulit dicari, tidak realtime, revisi berulang, file tercecer/hilang, salah input, dan tidak ada notifikasi otomatis. Divisi Administrasi adalah titik gesekan tertinggi karena menjadi hub penghubung hampir semua divisi lain namun bekerja dengan alat paling manual.

**Kesimpulan utama:** SAI membutuhkan ERP yang berpusat pada data pengujian dan dokumen (bukan sekadar akuntansi), dengan modul inti berupa: Quotation → Work Order → Sample Tracking → Hasil Uji (QC) → LHU → Invoice → Approval berjenjang → Dashboard monitoring — didukung oleh manajemen dokumen mutu (ISO 17025) dan kontrol akses berbasis peran per divisi. ERPNext dapat menjadi fondasi yang kuat untuk modul keuangan, penjualan, dan approval, namun modul teknis laboratorium (sample tracking, QC data pengujian, dan dokumen mutu ISO) memerlukan Custom App/DocType karena tidak ada modul bawaan yang secara native memodelkan alur kerja laboratorium lingkungan.

## 2. Company Overview

### 2.1 Profil Perusahaan

- **Nama:** PT Starlab Analitik Indonesia
- **Alamat:** Jl. Pangeran Sogiri, Ruko Millenium Kav-20, RT.005/003 Tanah Baru, Kec. Bogor Utara, Kota Bogor, Jawa Barat 16154
- **Bidang usaha:** Jasa laboratorium pengujian lingkungan (environmental testing laboratory) — pengujian kualitas udara, air, tanah/sedimen, kebisingan, dan emisi sumber bergerak/tidak bergerak.
- **Sertifikasi/Sistem Mutu:** Beroperasi dengan sistem dokumentasi mutu berjenjang khas ISO/IEC 17025 — Panduan Mutu (PM, Level 1), Prosedur Operasional (PO, Level 2), Instruksi Kerja Metode (IKM, Level 3), dan Dokumen Pendukung/Formulir (DP, Level 4). Terdapat ~29 dokumen PM, ~40+ dokumen PO, dan puluhan IKM per matriks pengujian (Udara Ambien, Udara Lingkungan Kerja, Emisi Sumber Tidak Bergerak, Emisi Gas Buang Kendaraan, Air Minum, dst).
- **Klien:** Korporat/institusi — contoh: PT Cipta Himayata (proyek Bandara Mentawai), Pusat Penelitian Kelapa Sawit, Berdikari, Ukailindo Kreasitama, Tresna Tjahya Nugraha, dsb (teridentifikasi dari mutasi rekening & work order).

### 2.2 Struktur Organisasi & Divisi

Berdasarkan kuesioner dan dokumen internal, divisi yang teridentifikasi:

| Divisi | Peran Utama | Direpresentasikan di Kuesioner? |
|---|---|---|
| Direksi (Dirut) | Persetujuan tertinggi, kebijakan | Tidak mengisi kuesioner (gap) |
| Manajer Mutu (MM) | Pengendalian dokumen mutu, monitoring kepatuhan | Ya (Shalma Pulung Hastiwi) |
| Manajer Teknis (MT) | Validasi hasil uji, monitoring pekerjaan lab | Ya (Komalasari) |
| Laboratorium / Analis | Eksekusi pengujian, input hasil, QC | Ya (Dzikri Fathul Alam) |
| Administrasi | Quotation, invoice, komunikasi klien, arsip | Ya (Astri Seventania, Eka Putri Agustin) |
| Finance / Akuntan | Pencatatan keuangan, rekonsiliasi bank | Ya (Dani Ramdani, freelance) |
| Marketing | Akuisisi klien | Tidak mengisi kuesioner (gap) |
| Client (eksternal) | Penerima layanan, approval quotation | N/A |

**Insight cross-document:** Dua dari delapan pemangku kepentingan kunci (Direksi dan Marketing) tidak memberikan input requirement — ini adalah gap signifikan karena Direksi muncul berulang sebagai approver akhir (kas operasional, quotation, dokumen mutu) dan Marketing menjadi sumber data awal proses penjualan.

> **Catatan pembaruan (lihat Bagian 14):** Status Marketing sebagai divisi/posisi yang berdiri sendiri — sebagaimana tercatat di tabel ini sejak awal — dikonfirmasi kembali benar pasca-BRA, setelah sempat "dikoreksi" di iterasi PRD pertengahan menjadi asumsi fungsi rangkap. Posisi ini tetap ada di struktur organisasi meski belum ada pemegang jabatan yang mengisi kuesioner saat BRA disusun.

### 2.3 Tujuan Bisnis

Dari saran-saran responden ("mohon dibuatkan gambaran sistem dari masukan tiap divisi", "diharapkan sistem dibuat tanpa mengganggu kegiatan rutin", "upload gambar jangan pdf saja") dapat disimpulkan tujuan implementasi ERP adalah: mendigitalisasi alur kerja lintas divisi tanpa mengganggu ritme kerja laboratorium yang sudah berjalan, meningkatkan visibilitas real-time atas status sample/pekerjaan/keuangan, dan mengurangi kesalahan input serta duplikasi dokumen.

### 2.4 Proses Bisnis Utama (ringkas)

```
Client → Marketing/Administrasi (Quotation) → Approval Client → Administrasi (Work Order)
→ Laboratorium (Sampling & Pengujian + QC) → Manajer Teknis (Validasi) → Manajer Mutu
(Pengendalian Dokumen LHU) → Administrasi (Invoice) → Finance (Penerimaan Pembayaran
& Rekonsiliasi) → Direksi (Approval kas/kebijakan) → Reporting.
```

## 3. Existing Business Process (As-Is) & Requirement per Divisi

### 3.1 Finance / Akuntan (Dani Ramdani — status freelance, bukan karyawan tetap)

- **Aktivitas utama:** Input data dari rekening koran & mutasi kas ke sistem internal (proses manual, hasil pengujian bukti transfer PDF → dicatat ulang).
- **As-Is:** Dokumen sumber = rekening koran bank Mandiri (PDF) yang berisi transaksi campur — gaji, ops sampling, DP klien, kasbon karyawan, pembayaran invoice klien — dalam satu mutasi tanpa kategorisasi akuntansi otomatis.
- **Pain points:** Sulit mencari data lama, data tidak realtime, komunikasi antar divisi lambat.
- **Bottleneck:** "Permintaan data" adalah bagian paling memakan waktu — mengindikasikan Finance sering diminta data ad-hoc oleh divisi lain tanpa akses mandiri ke laporan.
- **Risiko operasional:** Data keuangan bersifat rahasia namun saat ini diakses (view) oleh hampir semua divisi (Administrasi, Lab, MT, MM, Finance, Marketing, Direksi) — potensi kebocoran informasi finansial internal (gaji, kasbon) ke lini yang tidak seharusnya.
- **Kebutuhan sistem:** Laporan otomatis, notifikasi invoice jatuh tempo. Modul Invoice dinilai sangat penting; approval dianggap tidak diperlukan untuk pekerjaan input datanya sendiri.

### 3.2 Laboratorium / Analis (Dzikri Fathul Alam, Penyelia/Supervisor)

- **Aktivitas:** Input data, pengujian sample, approval, monitoring pekerjaan, pengelolaan stok, membuat laporan, validasi hasil, pengarsipan — cakupan kerja terluas di antara semua responden.
- **As-Is:** Menggunakan 8 tools berbeda sekaligus (Excel, WhatsApp, buku tulis, Word/PDF, Google Drive, Email, sistem internal, kertas/form manual) — indikasi kuat proses belum terstandardisasi ke satu platform.
- **Pain points:** Salah input data, data hilang, file tercecer.
- **Bottleneck:** Analisa tanah adalah pekerjaan paling memakan waktu (konsisten dengan bukti file C-Organik yang mensyaratkan perhitungan QC manual — kurva kalibrasi, ripitabilitas, %trueness — per sampel).
- **Dokumen kunci:** "List Work Order" (rekap pengujian, dikelola di Google Drive), berelasi dengan dokumen LHU.
- **Approval:** Membutuhkan approval dari MT; keterlambatan approval menyebabkan data menumpuk (backlog pekerjaan lab).
- **Kebutuhan sistem:** Tracking sample, dashboard realtime, monitoring stok, tracking status pekerjaan, laporan otomatis, reminder pekerjaan. Notifikasi stok reagen/bahan hampir habis.

### 3.3 Manajer Mutu / MM (Shalma Pulung Hastiwi)

- **Aktivitas:** Monitoring pekerjaan seluruh divisi, komunikasi klien, pengarsipan dokumen mutu.
- **As-Is:** Memahami alur kerja hanya sebagian ("Sebagian") — mengindikasikan kurangnya visibilitas lintas-divisi meski posisinya sebagai pengawas mutu.
- **Dokumen kunci:** Daftar Induk Dokumen Sistem Manajemen Mutu (PM/PO/IKM) — dokumen "hulu ke hilir" yang mengatur seluruh SOP laboratorium dan distribusinya ke Dirut, MM, MT, MK3.
- **Pain point:** Kurangnya monitoring; lupa bila ada dokumen revisi baru terbit — risiko kepatuhan (compliance risk) karena staf berpotensi bekerja dengan versi SOP yang sudah usang.
- **Approval:** Persetujuan dokumen dilakukan oleh Direksi; keterlambatan approval → arsip/penerbitan dokumen tertunda.
- **Kebutuhan sistem:** Upload/download dokumen terpusat, laporan otomatis, audit log, reminder pekerjaan, notifikasi dokumen revisi terbit.

### 3.4 Administrasi — Quotation & Client-Facing (Astri Seventania)

- **Aktivitas:** Input data, approval, invoice/tagihan, komunikasi klien, administrasi dokumen, pengarsipan — divisi dengan jumlah pain point terbanyak dari seluruh responden.
- **Bottleneck utama:** "Bikin penawaran" (membuat quotation) adalah pekerjaan paling memakan waktu — konsisten dengan bukti dokumen Quotation Quo-SAI/V/2026/076 yang menunjukkan tabel rincian parameter, regulasi acuan, frekuensi, qty per titik, dan harga satuan yang disusun manual per proyek.
- **Pain points:** Revisi berulang, sulit mencari data, file tercecer, input data berulang, tidak realtime, stok tidak terpantau.
- **Posisi strategis:** Divisi ini menerima data dari dan memberi data ke hampir semua divisi lain (Administrasi, Lab, MT, MM, Finance, Marketing, Client, Direksi) — menjadikannya hub informasi de facto perusahaan meski tanpa dukungan sistem yang memadai.
- **Approval:** Quotation memerlukan approval berlapis dari MT, MM, Finance, Marketing, dan Direksi — proses approval paling kompleks di antara seluruh dokumen yang teridentifikasi.
- **Kebutuhan sistem:** Tracking sample, approval digital, auto invoice, notifikasi otomatis, tracking status pekerjaan, histori client, reminder pekerjaan.

> **Catatan pembaruan (lihat Bagian 14):** Rantai approval quotation di atas adalah gambaran As-Is hasil kuesioner. Rantai approval final yang diimplementasikan di sistem sudah dikonfirmasi berbeda dari daftar As-Is ini — lihat Bagian 14 untuk detail.

### 3.5 Administrasi — Kas Operasional Harian (Eka Putri Agustin)

- **Aktivitas:** Input data & administrasi dokumen untuk laporan kas kecil operasional (bukti: Laporan Keuangan SAI - Operasional Harian 2026, mencatat transaksi kecil seperti beli kertas HVS, service saklar motor, makan siang anak magang, laundry).
- **Pain points:** Salah input data, revisi berulang, sulit mencari data.
- **Approval:** Oleh Direksi dan Finance; keterlambatan → pekerjaan tertunda.
- **Kebutuhan sistem:** Laporan otomatis; notifikasi approval pending.
- **Saran eksplisit:** Sistem sebaiknya mendukung upload gambar (foto struk), bukan hanya PDF — kebutuhan praktis di lapangan untuk pencatatan kas kecil.

> **Catatan pembaruan (lihat Bagian 14):** Approval kas kecil As-Is (Direksi dan Finance) berbeda dari keputusan final sistem (Direksi saja) — lihat Bagian 14.

### 3.6 Manajer Teknis / MT (Komalasari)

- **Aktivitas:** Monitoring pekerjaan dan validasi hasil uji.
- **As-Is:** Mengelola "List WO" dan "data hitung" (data perhitungan QC hasil uji, selaras dengan bukti file C-Organik yang berisi kurva kalibrasi, ripitabilitas, %trueness, dan hasil analisa per sampel — kalkulasi manual di Excel).
- **Pain point:** Tidak ada notifikasi otomatis atas perubahan status pekerjaan.
- **Approval:** Menariknya, approval pekerjaan MT dilakukan oleh Administrasi — pola ini berkebalikan dengan asumsi umum (biasanya MT yang mem-validasi sebelum data diteruskan ke Administrasi). (Lihat Bagian 8 — Gap/Konflik Antar Dokumen)
- **Dampak keterlambatan approval:** Sample terlambat diproses — risiko langsung terhadap SLA/target tanggal pengujian yang tercantum di Work Order.
- **Kebutuhan sistem:** Permintaan paling komprehensif di antara seluruh responden — tracking sample, dashboard realtime, approval digital, monitoring stok, upload/download dokumen, tracking status pekerjaan, histori client, laporan otomatis, reminder pekerjaan.
- **Catatan penting untuk change management:** "diharapkan sistem dibuat tanpa mengganggu kegiatan rutin pekerjaan" — sinyal eksplisit bahwa keberhasilan implementasi bergantung pada UX yang tidak menambah beban kerja lab harian.

## 4. Functional Requirements

| Kategori | Kebutuhan | Alasan Pengelompokan |
|---|---|---|
| Master Data | Data Klien, Katalog Parameter Uji & Regulasi Acuan (SNI/Permenkes/PP), Matriks Pengujian (Udara/Air/Tanah/Sedimen), Data Personel/Analis & kompetensinya, Data Peralatan Lab, Daftar Harga Satuan per parameter | Semua entitas ini adalah data referensi yang dipakai berulang di Quotation, WO, dan Hasil Uji |
| Transaction | Quotation (Surat Penawaran), Work Order/Permintaan Pengujian, Sampling & Penerimaan Sampel, Input Hasil Uji + data QC, LHU (Laporan Hasil Uji), Invoice, Pencatatan Kas Kecil, Mutasi Bank | Alur transaksional inti yang berulang tiap proyek pengujian |
| Approval | Approval Quotation (multi-divisi), Approval hasil uji lab (oleh MT), Approval dokumen mutu (oleh Direksi), Approval pengeluaran kas (Direksi & Finance) | Muncul di 5 dari 6 responden sebagai kebutuhan eksplisit |
| Reporting | Laporan Hasil Uji otomatis, Laporan Keuangan Operasional, Rekap Status Pengujian, Riwayat Klien | Disebut sebagai fitur "sangat penting" oleh 5 dari 6 responden |
| Dashboard | Dashboard monitoring pekerjaan lab realtime, Dashboard status sample, Dashboard stok reagen/consumable, Dashboard keuangan | Kebutuhan langsung dari Lab, MT, MM |
| Notification | Stok hampir habis, Approval pending, Invoice jatuh tempo, Dokumen revisi terbit, Reminder target pengujian | Setiap divisi menyebut jenis notifikasi berbeda |
| User Management | Role-based access per divisi, hak akses granular per jenis dokumen | Kebutuhan RBAC granular, bukan sekadar role generik |
| Integration | Rekonsiliasi mutasi rekening bank, kemungkinan notifikasi via WhatsApp | WhatsApp adalah media komunikasi de facto di semua divisi |
| Document Management | Kontrol dokumen mutu ISO dengan versioning, distribusi terkendali per bagian | Bukti Daftar Induk Dokumen menunjukkan struktur dokumen mutu formal 4-level |
| Audit Trail | Log riwayat perubahan dokumen mutu, log approval, log akses dokumen rahasia | Diminta eksplisit oleh MM; relevan untuk kepatuhan ISO/IEC 17025 |

## 5. Non-Functional Requirements

| Aspek | Kebutuhan | Justifikasi dari data |
|---|---|---|
| Security | Kontrol akses berbasis role & dokumen; enkripsi data finansial | Beberapa dokumen ditandai rahasia namun akses view saat ini terlalu luas |
| Role & Permission | Hak akses granular: Melihat/Menambah/Mengedit/Menghapus/Approve | Pola ini konsisten muncul di setiap jawaban kuesioner |
| Performance | Sistem harus responsif tanpa mengganggu ritme kerja | Permintaan eksplisit dari MT Direksi |
| Backup | Backup rutin data hasil uji dan dokumen mutu | Pain point "data hilang" muncul berulang |
| Availability | Ketersediaan tinggi untuk akses lapangan | Bukti dari Quotation: tim sampling bertugas di lokasi remote hingga 9 hari |
| Scalability | Sistem harus dapat menampung ratusan Work Order per tahun | Rekap Work Order 2026 mencatat >50 WO hanya dalam beberapa bulan pertama |
| Logging | Log aktivitas pengguna pada dokumen finansial dan mutu rahasia | Berkaitan dengan kebutuhan audit trail MM |
| Audit (ISO/IEC 17025) | Jejak revisi dokumen mutu harus dapat ditelusuri | Struktur dokumen menunjukkan pola edisi/revisi formal |
| Data Integrity | Data QC tidak boleh dapat diubah setelah divalidasi MT | Data ini menjadi dasar legal LHU |

## 6. Business Process Mapping

### 6.1 Alur Proses Utama (Core Value Chain)

```
Client → Marketing/Administrasi ──► Quotation (parameter, regulasi,
harga)
  │
  ▼
Approval Quotation (MT → MM → Finance → Marketing → Direksi)
  │
  ▼
Client Approval / PO
  │
  ▼
Administrasi ──► Work Order (No Project, Matriks, Parameter, ID
Sample, PJ Analis, Target Tanggal)
  │
  ▼
Laboratorium ──► Sampling + Penerimaan Sample
  │
  ▼
Laboratorium ──► Pengujian & Input Hasil + Data QC
  │
  ▼
Manajer Teknis ──► Validasi Hasil Uji
  │
  ▼
Manajer Mutu ──► Penerbitan LHU + Kontrol Dokumen
  │
  ▼
Administrasi ──► Invoice ke Client
  │
  ▼
Finance ──► Penerimaan Pembayaran, Rekonsiliasi
  │
  ▼
Direksi ──► Approval pengeluaran & kaji ulang manajemen
  │
  ▼
Reporting (Laporan Keuangan, Rekap Pengujian, Dashboard Monitoring)
```

> Catatan: rantai approval Quotation di atas adalah gambaran As-Is dari kuesioner — lihat Bagian 14 untuk rantai approval final yang diimplementasikan.

### 6.2 Hubungan Antar Divisi

- Administrasi adalah simpul pusat (hub) — satu-satunya divisi yang berinteraksi dengan seluruh divisi lain termasuk Client, sehingga menjadi titik kegagalan tunggal bila prosesnya masih manual.
- Laboratorium ↔ Manajer Teknis membentuk siklus kerja-validasi yang berulang untuk setiap sample.
- Manajer Mutu berperan lintas seluruh siklus sebagai pengendali dokumen dan kepatuhan, namun saat ini memiliki visibilitas paling rendah.
- Finance menerima data transaksi dari hampir semua sumber melalui satu rekening operasional campuran, tanpa pemisahan kategori otomatis.
- Direksi muncul sebagai approver akhir di banyak alur namun tidak memberikan input requirement.

## 7. Gap Analysis (As-Is vs To-Be)

| Area | As-Is | To-Be | Gap yang Harus Diselesaikan ERP |
|---|---|---|---|
| Media kerja | Excel + WhatsApp + Google Drive + kertas manual tersebar di 6+ tools | Satu platform terpusat | Konsolidasi data & proses ke satu sistem tanpa menghapus kebiasaan komunikasi WhatsApp |
| Pencarian data | Manual, lambat | Pencarian terpusat & terindeks | Modul dokumen & transaksi dengan pencarian/filter |
| Status pekerjaan | Tidak realtime, tidak ada notifikasi | Dashboard & notifikasi realtime | Modul Dashboard + Notification Engine |
| Approval | Manual (verbal/WA), berjenjang, tidak terlacak | Approval digital dengan workflow terdefinisi | Frappe Workflow terkonfigurasi + histori approval |
| Kontrol dokumen mutu | Daftar Induk dikelola manual di Excel | Document Management dengan versioning otomatis | Custom App Document Control |
| Data QC laboratorium | Perhitungan manual per file Excel | Template QC terstandardisasi | Custom DocType "Hasil Uji" |
| Stok/inventory | Tidak terpantau | Modul inventory dengan notifikasi stok minimum | Modul Stock/Item ERPNext + reorder alert |
| Kas & rekening | Rekening operasional tercampur tanpa kategori | Chart of Account terstruktur | Modul Accounting ERPNext + kategorisasi transaksi |
| Akses data sensitif | Akses lihat terlalu luas untuk dokumen rahasia | Kontrol akses granular | Role Permission Manager + audit log |

## 8. Gap/Konflik Antar Dokumen — Perlu Klarifikasi

Beberapa inkonsistensi ditemukan lintas dokumen yang perlu divalidasi ke narasumber sebelum desain sistem final:

1. **Arah approval MT vs Administrasi tidak konsisten.** Dzikri (Lab) menyatakan approval pekerjaannya dilakukan oleh MT. Namun Komalasari (MT sendiri) menyatakan approval pekerjaannya dilakukan oleh Administrasi — berlawanan dengan alur teknis yang wajar. Rekomendasi klarifikasi: konfirmasi ke MT dan Administrasi apakah "approval" di sini merujuk pada approval administratif (mis. pengeluaran WO baru) bukan approval teknis hasil uji. *(Status: masih terbuka — lihat Bagian 14.)*
2. **Klasifikasi kerahasiaan tidak sejalan dengan hak akses.** Dokumen Rekening Koran & Mutasi Kas ditandai rahasia oleh Finance, namun hak akses "Melihat data" diberikan ke hampir seluruh divisi. Rekomendasi: definisikan ulang matriks akses data finansial. *(Status: sebagian tertutup untuk Quotation — lihat Bagian 14; untuk rekening koran/mutasi bank secara luas masih terbuka.)*
3. **Cakupan divisi yang terlibat pada dokumen "List Work Order" berbeda-beda.** Dzikri menyebut divisi terlibat: Administrasi, Laboratorium, Manajer Teknis. Komalasari hanya menyebut Laboratorium. Rekomendasi: perlu satu definisi RACI tunggal per jenis dokumen. *(Status: masih terbuka.)*
4. **Dua pencatatan kas yang berpotensi tumpang tindih.** Rekening Koran mencatat transaksi bank resmi, sementara Laporan Kas Operasional Harian mencatat transaksi kas kecil terpisah. Rekomendasi: klarifikasi apakah kas kecil ini sub-akun dari rekening utama atau kas fisik terpisah. *(Status: RESOLVED — lihat Bagian 14, sudah diimplementasikan sebagai akun GL terpisah.)*
5. **Parameter dengan status "Subkon" pada Work Order** menunjukkan adanya proses subkontrak pengujian ke laboratorium eksternal yang belum tercakup jelas dalam requirement gathering manapun. Rekomendasi: perlu sesi klarifikasi khusus tentang alur kerja subkontraktor. *(Status: masih terbuka.)*

## 9. ERP Module Recommendation & Frappe/ERPNext Customization Mapping

**Kesimpulan arsitektur:** ERPNext core menangani mayoritas kebutuhan (Sales, Accounting, Stock, Workflow, Permission, Dashboard) melalui konfigurasi. Namun inti bisnis SAI — Work Order pengujian, sample tracking, data QC laboratorium, dan dokumen mutu ISO — memerlukan Custom App di Frappe Framework karena tidak ada padanan modul bawaan yang memodelkan proses laboratorium lingkungan secara akurat. Detail pemetaan lengkap per kebutuhan bisnis dapat dilihat di Technical Solution Design (TSD).

## 10. Implementation Roadmap

**Phase 1 — Fondasi & Quick Wins** (Finance & Administrasi): Master Data, Quotation + Workflow approval berjenjang, Sales Invoice + Payment Entry, Bank Reconciliation, Role & Permission dasar.

**Phase 2 — Inti Operasional Laboratorium:** Work Order Pengujian, Sample Tracking, Hasil Uji + kalkulasi QC, Dashboard monitoring lab, Notifikasi stok & target tanggal.

**Phase 3 — Kepatuhan, Dokumen Mutu & Ekspansi:** Document Control ISO 17025, Audit trail, Client Portal, Integrasi WhatsApp, Modul Inventory penuh.

*(Detail sprint-level ada di Technical Solution Design dan Project Plan.)*

## 11. Risks & Assumptions

**Kebutuhan Migrasi Data:** Riwayat Work Order, hasil uji, dan dokumen mutu tersebar di Google Drive dan Excel individual per staf — perlu audit & konsolidasi data sebelum migrasi.

**Kebutuhan Pelatihan Pengguna:** Divisi Laboratorium & MT terbiasa bekerja dengan kombinasi 8 tools berbeda — perlu pendekatan pelatihan bertahap dan sederhana.

**Perubahan Proses Bisnis:** Alur approval WO/hasil uji perlu diperjelas dan distandardisasi sebelum dikonfigurasi menjadi workflow digital.

**Risiko Implementasi:** Ketiadaan input dari Direksi dan Marketing dalam requirement gathering berisiko menghasilkan desain approval/dashboard yang tidak selaras dengan kebutuhan pengambil keputusan tertinggi. Proses subkontrak pengujian belum tercakup dalam requirement.

**Kebutuhan Validasi Lanjutan:** Wawancara terpisah dengan Direksi dan Marketing untuk melengkapi requirement. Sesi klarifikasi khusus untuk poin-poin konflik di Bagian 8.

## 12. Questions for Stakeholders

**Untuk Direksi:** Apa prioritas strategis Direksi terhadap sistem ERP ini? Data finansial apa saja yang harus dibatasi hanya untuk Direksi & Finance?

**Untuk Marketing:** Bagaimana proses akuisisi klien saat ini berjalan sebelum quotation dibuat?

**Untuk Manajer Teknis & Administrasi:** Siapa sebenarnya yang menyetujui pekerjaan Manajer Teknis? Apa definisi RACI resmi untuk dokumen "List Work Order"?

**Untuk Finance:** Apakah kas kecil operasional harian merupakan sub-akun dari rekening utama atau kas fisik terpisah? *(Sudah terjawab — lihat Bagian 14.)*

**Untuk Laboratorium & Manajer Mutu:** Bagaimana alur kerja subkontraktor pengujian? Berapa lama masa retensi sample sebelum dibuang?

## 13. Final Recommendation

1. Bangun di atas Frappe Framework/ERPNext, bukan membangun dari nol.
2. Investasi utama harus diarahkan ke Custom App laboratorium (Work Order Pengujian, Sample Tracking, Hasil Uji + QC, Document Control ISO).
3. Mulai dari Phase 1 (Finance & Administrasi) untuk quick win.
4. Selesaikan poin konflik/ambiguitas di Bagian 8 sebelum mengunci desain workflow approval final.
5. Libatkan Direksi dan Marketing secepatnya dalam putaran requirement gathering berikutnya.
6. Rancang kebijakan klasifikasi data sejak awal sebagai bagian dari desain Role Permission.

**Catatan metodologi:** Analisis ini disusun dari cross-referencing 1 kuesioner requirement gathering (6 responden) dengan 7 dokumen operasional internal. Asumsi yang digunakan telah ditandai secara eksplisit di sepanjang dokumen ini beserta rekomendasi klarifikasinya.

## 14. ADDENDUM — Pembaruan Pasca-BRA

Bagian ini mencatat keputusan dan informasi yang muncul setelah BRA awal disusun, hasil dari diskusi lanjutan dengan Product Owner selama tahap technical design dan development. BRA di atas (Bagian 1–13) dipertahankan apa adanya sebagai catatan historis hasil requirement gathering awal; bagian ini melengkapi, bukan menggantikan.

### 14.1 Rantai Approval Quotation — Keputusan Final

Rantai approval As-Is yang tercatat di Bagian 3.4 dan 6.1 (MT → MM → Finance → Marketing → Direksi, 5 tahap) **tidak dipakai** sebagai desain final sistem. Keputusan final yang dikonfirmasi langsung oleh Product Owner:

- Rantai approval Quotation: **MT → MM → Direksi** (tiga tahap).
- **Finance bukan approver** — hanya memiliki akses baca (read-only) untuk kebutuhan pelaporan keuangan internal.
- **Marketing juga bukan approver** — hanya memiliki akses baca (read-only) untuk visibilitas pipeline penjualan.
- Role Marketing (Bagian 2.2) tetap dipertahankan di sistem sebagai posisi standalone, meski belum ada pemegang jabatan aktif — antisipasi bila perusahaan merekrut posisi ini di kemudian hari.

### 14.2 Approval Kas Kecil — Keputusan Final

Approval kas kecil As-Is (Bagian 3.5: "Oleh Direksi dan Finance") juga **tidak dipakai** sebagai desain final. Keputusan final: approver Petty Cash Entry adalah **Direksi saja**. Finance tetap memiliki akses baca untuk keperluan pelaporan, tanpa peran approval.

### 14.3 Struktur Kas Kecil vs Rekening Utama — RESOLVED

Gap Bagian 8 Poin 4 (kas kecil vs rekening utama) sudah terjawab: kas kecil diimplementasikan sebagai akun General Ledger terpisah ("Kas Kecil"), berbeda dari rekening operasional utama, konsisten dengan format Laporan Keuangan Operasional Harian yang sudah berjalan.

### 14.4 Client Dashboard

Client dapat memantau status pekerjaan dan mengunduh LHU melalui halaman tracking berbasis **nomor pesanan, tanpa perlu login/akun**. Tidak ada fungsi approval di halaman ini.

### 14.5 Requirement Baru: Inventaris Reagen & Peralatan

Ditemukan kebutuhan yang belum tercatat di Bagian 4 (Functional Requirements): inventaris perlu dipisah menjadi dua kategori dengan kebutuhan pelacakan berbeda:

- **Reagen/bahan kimia (LIMS):** perlu pelacakan tanggal kedaluwarsa dan tanggal masuk per batch.
- **Peralatan kantor/lab:** perlu pelacakan tanggal kalibrasi, relevan untuk kepatuhan ISO/IEC 17025.

Detail desain awal ada di Technical Solution Design Bagian 4.13. Frekuensi kalibrasi standar per jenis alat dan cakupan pelacakan untuk peralatan non-lab masih perlu diklarifikasi ke Manajer Teknis/Manajer Mutu.

### 14.6 Gap yang Masih Terbuka

Poin 1, 2, 3, dan 5 di Bagian 8 sudah terjawab per 2026-07-30 — lihat Bagian 14.8–14.11. Yang masih belum terklarifikasi dan tetap perlu ditindaklanjuti:

- Wawancara langsung ke Direksi dan pemegang fungsi Marketing untuk melengkapi requirement gathering awal.

### 14.7 Keputusan Operasional Tambahan

Rangkaian klarifikasi lanjutan ke Product Owner menghasilkan sejumlah keputusan operasional konkret yang melengkapi Bagian 3 dan 4: masa berlaku quotation menjadi 45 hari (dapat diaktifkan kembali bila kedaluwarsa), revisi quotation setelah sebagian disetujui mengharuskan pengulangan approval dari awal, pencatatan awal (Form A) wajib untuk seluruh quotation, tarif biaya percepatan (rush fee) mengikuti dua tingkatan tetap, dan syarat pelunasan invoice adalah 7 hari kalender setelah invoice terbit. Field "Accurate" yang sempat ambigu dikonfirmasi merujuk pada sistem akuntansi Finance. Detail lengkap ada di PRD Quotation & Master Data v8 dan TSD v4.

### 14.8 Arah Approval Work Order — RESOLVED

Gap Bagian 8 Poin 1 (arah approval MT vs Administrasi, kontradiksi antar narasumber) sudah terjawab: bukan satu aturan tunggal, tergantung jenis approval-nya.

- Kerjaan teknis harian (raw data, hasil hitung) — tidak ada approval sampai manajemen puncak, cukup dari Penyelia ke Manajer Teknis.
- Pengadaan barang / kalibrasi — approval ke Manajer Mutu.
- LHU — pengesahan ke Direktur.
- Work Order ke subkontraktor eksternal — approval ke Manajer Mutu dan Direktur (lihat Bagian 14.9).
- Ada audit tahunan silang antara Teknis dan Mutu (Teknis audit Mutu, Mutu audit Teknis) — ini audit kepatuhan berkala, bukan approval per-transaksi.
- Kerjaan harian secara umum tidak butuh approval atasan, cuma beberapa form tertentu saja.

Perlu direview terhadap Workflow "Work Order Pengujian" yang sudah berjalan, apakah state/transition yang ada sekarang sudah sesuai pembagian ini.

### 14.9 Alur Kerja Subkontraktor Pengujian — RESOLVED

Gap Bagian 8 Poin 5 (F0-5) sudah terjawab: Manajer Teknis meminta ke Administrasi untuk membuatkan form Work Order ke laboratorium subkontraktor. Form disetujui oleh Manajer Mutu dan Direktur. Pemantauan progress mengacu ke estimasi hari kerja lab penguji eksternal; hasilnya di-follow up oleh Administrasi.

### 14.10 RACI Dokumen "List Work Order" — RESOLVED

Gap Bagian 8 Poin 3 sudah terjawab: divisi yang terlibat adalah Administrasi dan Manajer Teknis.

### 14.11 Matriks Akses Data Finansial — RESOLVED

Gap Bagian 8 Poin 2 sudah terjawab: akses data finansial sensitif (Rekening Koran, Mutasi Kas) dibatasi hanya untuk Finance dan Direksi, bukan seluruh divisi seperti kondisi sekarang.

---

*Dokumen BRA ini, beserta Addendum di atas, menjadi basis penyusunan Technical Solution Design dan Product Requirement Document (PRD) modul Quotation & Master Data v8.*
