# TECHNICAL SOLUTION DESIGN (TSD)

## Implementasi ERP dengan Frappe Framework & ERPNext — PT Starlab Analitik Indonesia

**Disusun oleh:** Senior ERP Solution Architect / Frappe Technical Architect / ERPNext Implementation Consultant

**Versi Dokumen:** 3.0

**Basis dokumen:** Business Requirement Analysis (BRA) — Pengembangan Sistem ERP PT Starlab Analitik Indonesia; Product Requirement Document (PRD) — Modul Quotation & Master Data v8

**Ruang lingkup:** Blueprint teknis siap-implementasi di atas Frappe Framework v15 + ERPNext, mencakup seluruh modul inti SAI: Master Data, Quotation, Work Order Pengujian, Sample Tracking, Hasil Uji/QC, LHU, Invoice/Keuangan, Dokumen Mutu ISO 17025, dan Client Dashboard.

---

## BAB 1 — SOLUTION ARCHITECTURE

### 1.1 Gambaran Arsitektur Sistem Secara Keseluruhan

Solusi dirancang dengan prinsip "ERPNext Core sebagai fondasi transaksi generik (Sales, Accounting, Stock, Permission, Workflow) + Custom App sebagai lapisan domain-spesifik laboratorium lingkungan". Pendekatan ini memaksimalkan konfigurasi native, dan hanya membangun custom development pada area yang tidak dipenuhi modul bawaan.

```
┌─────────────────────────────────────────────────────────────────┐
│ PRESENTATION LAYER                                                │
│ Frappe Desk (internal user)  │  Website SAI (WordPress) —         │
│                               │  Client Dashboard (read-only)      │
└───────────────────────────────┬───────────────────────────────────┘
                                 │
┌───────────────────────────────▼───────────────────────────────────┐
│ APPLICATION LAYER (Frappe Framework)                               │
│ ┌───────────────────────┐   ┌─────────────────────────────────┐  │
│ │ ERPNext CORE           │◄─►│ CUSTOM APPS                      │  │
│ │ (native, konfigurasi)  │   │ (domain-spesifik SAI)             │  │
│ │                        │   │                                   │  │
│ │ - Selling (Quotation,  │   │ 1. starlab_customizations          │  │
│ │   Customer, Sales      │   │    Master Data & Quotation:        │  │
│ │   Invoice)             │   │    Client Inquiry, Kaji Ulang       │  │
│ │ - Accounting           │   │    Tender, T&C Template, Petty      │  │
│ │ - Stock                │   │    Cash Entry                       │  │
│ │ - HR (Employee)        │   │ 2. starlab_lab_ops                  │  │
│ │ - Workflow Engine      │   │    Work Order, Sample, Test         │  │
│ │ - Role Permission Mgr  │   │    Result, LHU                      │  │
│ │ - Notification Fwk     │   │ 3. starlab_quality                  │  │
│ │ - Print Format Builder │   │    Document Control ISO 17025       │  │
│ │ - Translation          │   │ 4. starlab_integrations             │  │
│ │                        │   │    WhatsApp Gateway, REST API       │  │
│ │                        │   │    Client Dashboard                 │  │
│ └───────────────────────┘   └─────────────────────────────────┘  │
└───────────────────────────────┬───────────────────────────────────┘
                                 │
┌───────────────────────────────▼───────────────────────────────────┐
│ DATA LAYER (MariaDB)                                                │
│ Single database — semua DocType (core & custom) satu schema        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Modul Native ERPNext yang Digunakan

| Modul Native | Fungsi dalam Solusi |
|---|---|
| Selling | Customer master, Quotation, Sales Invoice |
| Accounting | Chart of Account, Payment Entry, Journal Entry (Kas Kecil), Bank Reconciliation Tool, Bank Statement Import |
| Stock | Item Master (reagen/consumable), Reorder Level & Reorder Qty, Stock Entry |
| HR (ringkas) | Employee master, digunakan sebagai referensi PJ Analis, MT, MM |
| Workflow | State machine approval untuk Client Inquiry, Quotation, Work Order, Sample, Test Result, Document Control, Invoice, Petty Cash |
| Role Permission Manager | RBAC granular per DocType per role |
| Notification | Trigger notifikasi berbasis event/kondisi |
| Print Format Builder | Template Quotation, LHU, Invoice |
| Translation | Lokalisasi label UI ke Bahasa Indonesia, sementara nama teknis (DocType, field, API) tetap Bahasa Inggris |
| Data Import Tool | Migrasi data historis dari Excel/Google Drive ke DocType baru |

### 1.3 Custom App

Empat Custom App dibangun sesuai prinsip "satu app per domain fungsional" agar mudah dipelihara dan di-deploy terpisah bila diperlukan:

1. **starlab_customizations** — mencakup seluruh modul Master Data dan Quotation, termasuk pra-quotation: Custom Field/Child Table pada Quotation, Custom Field pada Customer dan Sales Invoice, DocType Client Inquiry, Kaji Ulang Permintaan/Tender, T&C Master Template, dan Petty Cash Entry.
2. **starlab_lab_ops** — inti operasional laboratorium: Work Order Pengujian, Sample, Test Result (QC), LHU.
3. **starlab_quality** — Document Control sistem manajemen mutu ISO/IEC 17025 (PM/PO/IKM/DP).
4. **starlab_integrations** — Server Script & REST endpoint untuk integrasi WhatsApp Business API/gateway pihak ketiga, serta REST API yang menyediakan status tracking dan tautan unduh LHU untuk Client Dashboard.

Hanya keempat custom app di atas yang dikelola dalam *version control* (repository GitHub perusahaan). Source code core Frappe/ERPNext tidak di-*vendor* — ditarik melalui `bench get-app` mengikuti praktik standar ekosistem Frappe, karena tidak ada kebutuhan khusus (air-gapped deployment, compliance internal) yang mengharuskan vendoring penuh.

### 1.4 Hubungan ERPNext Core dan Custom App

- Custom DocType di `starlab_lab_ops` mereferensikan DocType core via Link Field (mis. Work Order Pengujian → Customer, Work Order Pengujian → Quotation, Work Order Pengujian → Employee).
- Sales Invoice (core) mereferensikan balik ke Work Order Pengujian (custom) via Custom Field `work_order_pengujian`, sehingga penagihan tetap memakai mesin Accounting native ERPNext.
- Client Inquiry, Kaji Ulang Permintaan/Tender, dan T&C Master Template (`starlab_customizations`) membentuk rantai pra-quotation yang bermuara ke Quotation (Selling, core) melalui Link Field.
- Document Control (`starlab_quality`) berdiri independen dari alur transaksi Sales/Lab, terhubung ke Employee (core) sebagai `distributed_to` dan ke Role (core) untuk kontrol akses.
- Semua app berjalan dalam satu Frappe site/bench, berbagi satu database — tidak ada duplikasi data, hanya pemisahan source code per domain.

### 1.5 Client Dashboard — Arsitektur & Ketergantungan

Client Dashboard adalah halaman pelacakan status pekerjaan dan pengunduhan LHU yang diakses klien menggunakan ID pesanan (nomor Quotation/Work Order), bersifat read-only tanpa autentikasi transaksional. Halaman ini berada di website SAI (`starlabanaltikind.com`) yang berjalan di atas WordPress, bukan bagian dari Frappe Desk maupun Frappe Portal.

Arsitektur integrasinya terdiri dari dua sisi:

1. **Sisi Frappe** — REST endpoint *whitelisted* pada `starlab_integrations` yang menerima ID pesanan dan mengembalikan status tracking serta tautan unduh LHU. Bagian ini dapat dirancang dan diimplementasikan secara independen.
2. **Sisi WordPress** — halaman/plugin yang memanggil endpoint tersebut dan menampilkan hasilnya ke klien. Pekerjaan ini membutuhkan akses admin/hosting panel pada website live, yang kepemilikannya perlu dipastikan lebih dulu oleh tim internal sebelum pengerjaan dapat dimulai (lihat Bab 12, Sprint 10, dan Bab 13).

## BAB 2 — ERP MODULE MAPPING

| Kebutuhan Bisnis | Modul ERPNext | Konfigurasi? | Custom DocType? | Custom App? | Alasan |
|---|---|---|---|---|---|
| Master Data Klien | Selling — Customer | Ya | Tidak (custom field) | starlab_customizations | Customer DocType native sudah lengkap; tambah field industri/PIC dan kategori pelanggan |
| Katalog Parameter Uji & Regulasi | Custom DocType | Sebagian | Ya — Test Parameter | starlab_lab_ops | Item DocType native berorientasi barang dagang; parameter uji butuh field regulasi acuan, satuan, metode |
| Client Inquiry (Form A) | — | Tidak | Ya — Client Inquiry | starlab_customizations | Mencatat permintaan awal client (telepon/WA) sebelum quotation dibuat; tidak ada padanan modul native |
| Kaji Ulang Permintaan/Tender | — | Tidak | Ya — Kaji Ulang Tender | starlab_customizations | Penilaian kelayakan teknis oleh Manajer Teknis atas Client Inquiry |
| Quotation (Surat Penawaran) | Selling — Quotation | Ya + Custom Field | Tidak (custom child table) | starlab_customizations | Header/approval Quotation native cukup; tambahkan child table dan field pendukung (parameter, diskon, biaya kirim, rush fee, referensi Form A, T&C, cover, Lampiran A1) |
| Syarat & Ketentuan (T&C) | — | Tidak | Ya — T&C Master Template | starlab_customizations | Template statis institusional, hanya diubah di level master, bukan per-dokumen |
| Work Order Pengujian | — | Tidak | Ya — Work Order Pengujian | starlab_lab_ops | Struktur data (matriks, ID sample, PJ analis, target tanggal) tidak match dengan Work Order manufaktur bawaan |
| Sample Tracking & Chain of Custody | — | Tidak | Ya — Sample | starlab_lab_ops | Lifecycle sample lab lingkungan tidak ada modul setara di ERPNext core |
| Hasil Uji + Data QC | — | Tidak | Ya — Test Result | starlab_lab_ops | Perlu kalkulasi otomatis dan status lock pasca-approval |
| LHU (Laporan Hasil Uji) | Print Format Builder | Ya (untuk cetak) | Ya — LHU | starlab_lab_ops | Dokumen resmi rekap Test Result per Work Order |
| Invoice | Accounting — Sales Invoice | Ya + Custom Field | Tidak | starlab_customizations | Native, digenerate otomatis dari Work Order/LHU |
| Rekonsiliasi Bank | Accounting — Bank Reconciliation Tool | Ya | Tidak | Tidak | Native — import rekening koran untuk pencocokan otomatis |
| Kas Kecil / Petty Cash | Accounting — Journal Entry/Payment Entry | Sebagian | Ya — Petty Cash Entry | starlab_customizations | UX input harian oleh non-akuntan lebih baik lewat DocType ringan yang men-generate Journal Entry di belakang layar |
| Approval Berjenjang | Workflow | Ya | Tidak | Tidak | Frappe Workflow Engine menangani seluruh state machine per jenis dokumen |
| Dokumen Mutu ISO (PM/PO/IKM/DP) | — | Tidak | Ya — Document Master, Document Revision | starlab_quality | Kebutuhan versioning formal dan distribusi terkendali tidak dipenuhi modul File bawaan |
| Notifikasi | Notification | Ya + Server Script | Tidak | starlab_integrations (trigger custom) | Notification framework native cukup fleksibel; trigger custom (stok minimum, target tanggal, eskalasi SLA) perlu Server Script kecil |
| Integrasi WhatsApp | — | Tidak | Tidak (REST endpoint) | starlab_integrations | Tidak ada integrasi native, perlu webhook/API call ke gateway pihak ketiga |
| Client Dashboard | — | Tidak (di luar Frappe) | Tidak | starlab_integrations (REST API) | Halaman eksternal di website WordPress SAI yang memanggil REST API Frappe; bergantung pada akses admin situs live |
| Dashboard Monitoring | Frappe Dashboard/Insights | Ya | Tidak | Tidak | Native, dibangun di atas data Work Order/Sample/Test Result/Quotation |
| Role & Permission Granular | Role Permission Manager | Ya | Tidak | Tidak | Native, memetakan role ke seluruh divisi |
| Inventory Reagen | Stock — Item + Reorder Level | Ya | Tidak | Tidak | Native, cukup setting reorder level per item |
| Audit Trail | Version (native, Track Changes) | Ya | Tidak | Tidak | Aktif otomatis untuk seluruh DocType termasuk custom |

Dari seluruh kebutuhan bisnis di atas, mayoritas dipenuhi melalui konfigurasi native ERPNext, sementara diferensiasi bisnis SAI — Work Order pengujian, sample tracking, data QC laboratorium, dokumen mutu ISO, serta alur pra-quotation dan Client Dashboard — memerlukan Custom App di Frappe Framework.

## BAB 3 — CUSTOM APP DESIGN

### 3.1 starlab_customizations

**Tujuan:** Menampung seluruh modul Master Data dan siklus hidup Quotation (termasuk pra-quotation), serta seluruh penyesuaian ringan di atas DocType core ERPNext, tanpa mengubah source code ERPNext itu sendiri.

**Ruang lingkup:**
- Custom Field & Custom Child Table pada Quotation: rincian parameter/regulasi/frekuensi/qty/harga, diskon, biaya kirim, rush fee, referensi Client Inquiry, referensi T&C Master Template, cover/company profile, Lampiran A1, histori LHU klien.
- Custom Field pada Customer: jenis industri/PIC, kategori pelanggan.
- Custom Field pada Sales Invoice: Link Work Order Pengujian.
- DocType Client Inquiry (Form A).
- DocType Kaji Ulang Permintaan/Tender.
- DocType T&C Master Template.
- DocType Petty Cash Entry, yang men-generate Journal Entry di background via Server Script.

**Alasan dibuat:** Memisahkan customization dari core agar aman saat upgrade ERPNext, dan agar tim developer dapat melacak seluruh penyesuaian bisnis SAI — mulai dari penangkapan permintaan awal client hingga penagihan — dalam satu tempat.

### 3.2 starlab_lab_ops

**Tujuan:** Mendigitalkan inti proses laboratorium — dari penerimaan Work Order sampai penerbitan LHU.

**Ruang lingkup:** DocType Test Parameter (master), Work Order Pengujian, Sample, Test Result (QC), LHU. Termasuk Server Script kalkulasi QC (kurva kalibrasi, %RPD ripitabilitas, %trueness) dan logic status lock pasca-validasi.

**Alasan dibuat:** Ini adalah diferensiasi bisnis utama SAI — tidak ada modul ERPNext bawaan yang memodelkan matriks pengujian, rentang ID sample, dan perhitungan QC laboratorium lingkungan.

### 3.3 starlab_quality

**Tujuan:** Mengelola dokumen sistem manajemen mutu ISO/IEC 17025 (Panduan Mutu/Prosedur Operasional/Instruksi Kerja Metode/Dokumen Pendukung).

**Ruang lingkup:** DocType Document Master (metadata + file utama), Document Revision (log riwayat revisi), Document Distribution (child table distribusi terkendali per divisi + acknowledgement).

**Alasan dibuat:** Kebutuhan versioning formal, distribusi terkendali, dan notifikasi revisi adalah kebutuhan compliance spesifik yang tidak dipenuhi modul File generik Frappe.

### 3.4 starlab_integrations

**Tujuan:** Menjembatani notifikasi sistem ke kanal komunikasi dominan staf SAI (WhatsApp), serta menyediakan lapisan API bagi Client Dashboard di website eksternal.

**Ruang lingkup:** REST endpoint/Server Script yang dipanggil oleh Notification Framework native untuk meneruskan pesan ke WhatsApp Business API/gateway pihak ketiga; REST endpoint whitelisted untuk Client Dashboard (status tracking + tautan unduh LHU berdasarkan ID pesanan); konfigurasi kredensial tersimpan di Custom DocType Single "WhatsApp Settings" dan "Client Dashboard API Settings".

**Alasan dibuat:** Mengurangi risiko resistensi adopsi dengan mengirim notifikasi ke kanal yang sudah familiar bagi staf, serta memenuhi janji visibilitas status pekerjaan kepada klien tanpa harus membangun ulang Client Portal di Frappe.

## BAB 4 — DOCTYPE DESIGN

Seluruh DocType custom di bawah menggunakan Naming Series untuk penomoran otomatis, dan mengaktifkan Track Changes (audit trail native).

### 4.1 Customer (Master Data — perluasan)

Perluasan DocType Customer ERPNext dengan field tambahan:

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| pic_name | PIC | Data | Tidak |
| kategori_pelanggan | Kategori Pelanggan | Select (Perusahaan/Individu-Perorangan/Institusi Pemerintah/Universitas-Sekolah/Lain-lain) | Tidak |

**[RESOLVED]** Field `jenis_industri` yang sebelumnya dibuat terpisah sudah dikonfirmasi oleh Product Owner **identik** dengan `kategori_pelanggan` — dikonsolidasikan menjadi satu field saja. Bila field `jenis_industri` sudah lanjur dibuat di database produksi, perlu migrasi data (pindahkan isian ke `kategori_pelanggan`) lalu hapus field lama.

### 4.2 Test Parameter (Master Data — starlab_lab_ops)

**Tujuan:** Katalog parameter uji & regulasi acuan sebagai referensi Quotation, Work Order, dan Test Result. **Parent Module:** starlab_lab_ops

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| parameter_name | Nama Parameter | Data | Ya |
| matriks | Matriks | Select (Udara Ambien/Udara Emisi/Air Permukaan/Air Bersih/Air Limbah/Tanah/Sedimen/Kebisingan) | Ya |
| regulasi_acuan | Regulasi Acuan | Data (mis. PP No.22 Tahun 2021 Lamp. VI) | Ya |
| metode_uji | Metode Uji | Link → Document Master | Tidak |
| satuan | Satuan | Data | Ya |
| harga_satuan_default | Harga Satuan Default | Currency | Tidak |
| status | Status | Select (Aktif/Nonaktif) | Ya |

**Relationship:** Direferensikan oleh Quotation Parameter Detail (child table), WO Parameter Detail (child table), Test Result.

### 4.3 Client Inquiry (Form A) — starlab_customizations

**Tujuan:** Mencatat permintaan awal client (telepon/WA) sebelum quotation dibuat.

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| naming_series | Naming Series | Select | Ya |
| nama_pt | Nama PT/Instansi | Data | Ya |
| customer | Klien (jika sudah terdaftar) | Link → Customer | Tidak |
| alamat | Alamat | Small Text | Ya |
| pic_nama | PIC & Kontak | Data | Ya |
| matriks | Matriks Pengujian | Select | Ya |
| parameter_diminta | Parameter Diminta | Table (child, Link → Test Parameter) | Ya |
| regulasi_acuan | Regulasi Acuan (jika disebutkan client) | Data | Tidak |
| estimasi_qty | Estimasi Qty | Int | Tidak |
| channel_asal | Channel Asal | Select (Telepon/WA/Email/Lainnya) | Ya |
| catatan | Catatan Tambahan | Small Text | Tidak |
| dicatat_oleh | Dicatat Oleh | Link → Employee | Ya |
| status | Status | Select (Draft/Diajukan Kaji Ulang/Disetujui MT/Ditolak MT) | Ya |

**Relationship:** Client Inquiry 1—1 Kaji Ulang Tender; Client Inquiry 1—N Quotation.

### 4.4 Kaji Ulang Permintaan/Tender — starlab_customizations

**Tujuan:** Penilaian kelayakan teknis oleh Manajer Teknis atas Client Inquiry sebelum Quotation dibuat.

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| client_inquiry | Referensi Client Inquiry | Link → Client Inquiry | Ya |
| dinilai_oleh | Dinilai Oleh | Link → Employee | Ya |
| tanggal_kaji | Tanggal Kaji Ulang | Date | Ya |
| rekomendasi | Rekomendasi | Select (Layak/Tidak Layak/Layak dengan Catatan) | Ya |
| catatan_kelayakan | Catatan Kelayakan | Small Text | Tidak |

**Logic:** Saat `rekomendasi` disimpan sebagai "Layak" atau "Layak dengan Catatan", Client Inquiry terkait otomatis berpindah status menjadi "Disetujui MT" dan sebuah Quotation Draft baru dibuat otomatis dengan data (klien, parameter, matriks, regulasi, qty) ter-*prefill* dari Client Inquiry. Jika hasil penilaian "Tidak Layak", Client Inquiry berpindah ke status "Ditolak MT".

### 4.5 T&C Master Template — starlab_customizations

**Tujuan:** Menyimpan template Syarat & Ketentuan (12 poin standar SAI) yang di-*render* otomatis saat cetak Quotation.

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| versi_template | Versi Template | Data | Ya |
| berlaku_sejak | Berlaku Sejak | Date | Ya |
| konten_tnc | Konten T&C | Text Editor | Ya |
| diubah_oleh | Diubah Oleh | Link → Employee (read-only) | Tidak |

Isi minimal 12 poin standar: masa berlaku penawaran **45 hari kalender**; mekanisme quotation disetujui+stempel menjadi PO; dasar perhitungan harga = jumlah sampel aktual; konfirmasi jadwal sampling maksimal 2 hari kerja setelah PO dan Lampiran A1 diterima; ketentuan keterlambatan/pembatalan sampling; proses LHU (draft 10 hari kerja, review client 3 hari kerja, cetak dan tanda tangan final); dokumen penagihan dikirim maksimal 3 hari setelah pengambilan sampel selesai; syarat pembayaran (DP 50% untuk nilai ≥ Rp10.000.000, **pelunasan maksimal 7 hari kalender setelah invoice terbit**); batas revisi faktur pajak dan PPh23; jam penerimaan sampel; retensi sampel sisa; ketentuan pembatalan PO.

**[RESOLVED]** Masa berlaku penawaran diperbarui dari 30 hari menjadi **45 hari** (konsisten dengan field `tanggal_kedaluwarsa` di Quotation, Bab 4.6). Syarat pelunasan diperbarui dari "maksimal 30 hari kalender" menjadi **maksimal 7 hari kalender setelah invoice terbit** — dikonfirmasi Product Owner sebagai Term of Payment (TOP) yang berlaku, terpisah dari DP 50% di muka.

Template disimpan sebagai satu entitas institusional dengan histori versi — setiap perubahan tercatat melalui Track Changes, dan Quotation yang sudah terbit tetap merujuk versi T&C yang berlaku saat itu, bukan selalu versi terbaru. Hak mengubah konten template berada sepenuhnya pada Administrasi di level institusional; tidak ada mekanisme untuk mengedit T&C per-dokumen quotation individual.

### 4.6 Quotation — Custom Field & Child Table

Perluasan Quotation (Selling) ERPNext:

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| client_inquiry | Referensi Form A | Link → Client Inquiry | **Ya** |
| wo_parameter_detail | Detail Parameter | Table (child: Matriks, Parameter, Regulasi Acuan, Frekuensi, Qty per Titik, Harga Satuan, Harga Total) | Ya |
| discount_percent | Discount (%) | Percent | Tidak |
| biaya_kirim | Biaya Kirim | Currency | Tidak |
| tingkat_percepatan | Tingkat Percepatan (Rush Fee) | Select (Normal / 7 Hari Kerja (+80%) / 5 Hari Kerja (+100%) / Lainnya — Input Manual) | Tidak |
| rush_fee_hari | Rush Fee — Hari Percepatan (auto-fetch dari pilihan di atas, atau manual bila "Lainnya") | Int | Tidak |
| rush_fee_percent | Rush Fee — Persentase Tambahan (auto-fetch dari pilihan di atas, atau manual bila "Lainnya") | Percent | Tidak |
| tnc_template | Referensi T&C Master Template | Link → T&C Master Template | Ya |
| cover_file | Cover/Company Profile | Attach | Ya |
| lampiran_a1 | Lampiran A1 (kosong, untuk dicetak) | Attach | Tidak |
| lampiran_a1_terisi | Lampiran A1 — Hasil Isian Client (dikelola Administrasi) | Attach | Tidak |
| histori_lhu_klien | Referensi Histori LHU/Pekerjaan Klien | Table (read-only, fetch dari modul LHU) | Tidak |
| tanggal_terbit | Tanggal Terbit | Date | Ya |
| tanggal_kedaluwarsa | Tanggal Kedaluwarsa (auto = tanggal_terbit + 45 hari) | Date (read-only) | Ya |
| syarat_pembayaran | Syarat Pembayaran (DP %, Termin) | Data | Ya |

Field ringkasan harga mengikuti urutan: **Sub Total → Discount (%) → DPP → PPN (%) → Biaya Kirim → Total Invoice**. Kewajaran nilai Discount (%) menjadi tanggung jawab Administrasi untuk dipastikan sebelum quotation diajukan ke rantai approval — sistem tidak melakukan validasi otomatis atas kewajaran diskon, murni tanggung jawab proses manual.

**[RESOLVED]** Referensi Client Inquiry (`client_inquiry`) sekarang **wajib diisi** — dikonfirmasi Product Owner bahwa seluruh Quotation harus melalui pencatatan awal Form A terlebih dahulu, termasuk untuk client langganan/repeat. Tidak ada lagi jalur pembuatan Quotation langsung tanpa Form A.

**[RESOLVED]** Tingkat Percepatan (Rush Fee): dua tingkatan sudah dikonfirmasi — percepatan ke **5 hari kerja** dikenakan tambahan **100%** dari harga dasar, percepatan ke **7 hari kerja** dikenakan tambahan **80%**. Tier lain (percepatan ke jumlah hari selain 5 atau 7) belum ada aturan bakunya — gunakan opsi "Lainnya" dengan input manual, dan tandai untuk klarifikasi lanjutan bila ditemukan pola tier lain di kemudian hari.

Cover/Company Profile diimplementasikan sebagai satu file PDF standar (identitas perusahaan, ruang lingkup layanan, galeri kegiatan) yang sama untuk seluruh quotation dan digabungkan otomatis di depan setiap cetakan final — Administrasi tidak perlu menginput ulang setiap kali.

Field `tanggal_kedaluwarsa` dihitung otomatis melalui Server Script saat penyimpanan (45 hari sejak `tanggal_terbit`). `lampiran_a1` (kosong) disertakan otomatis pada Print Format final sebagai bagian keempat dari dokumen. **[RESOLVED]** Field `lampiran_a1_terisi` — data isian balik dari client dikonfirmasi tetap ditangani oleh **Administrasi**, dalam modul Quotation ini (bukan berpindah ke modul Work Order/Sample Tracking).

Print Format final menggabungkan empat komponen menjadi satu dokumen: Cover/Company Profile, Syarat & Ketentuan, tabel harga dinamis, dan Lampiran A1 kosong — dapat dicetak langsung dalam satu klik tanpa perlu proses export dan buka aplikasi lain.

### 4.7 Work Order Pengujian (Transaction — starlab_lab_ops)

**Tujuan:** Mendigitalkan dokumen "Permintaan Pengujian (Work Order)" — menggantikan form kertas manual DP-SAI-04-7.1-03F.

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| naming_series | Naming Series | Select (P.SAI.####.MM.YYYY) | Ya |
| customer | Klien | Link → Customer | Ya |
| quotation | Referensi Quotation | Link → Quotation | Tidak |
| kegiatan | Kegiatan | Data | Ya |
| tanggal_wo | Tanggal WO | Date | Ya |
| status | Status | Select (Draft/Approved/In Progress/Completed/Cancelled) | Ya |
| penerimaan_sampel | Diterima Oleh | Link → Employee | Ya |
| catatan | Catatan | Small Text | Tidak |
| wo_parameter_detail | Detail Parameter | Table → WO Parameter Detail (child) | Ya |

**Child Table — WO Parameter Detail:** matriks, parameter (Link → Test Parameter), sample_id_range, pj_analis (Link → Employee), target_pengujian (Date), status_pengujian (Select: Pending/In Progress/Done/Subkon), keterangan.

**Relationship:** Work Order Pengujian 1—N Sample; Work Order Pengujian → Customer (N—1); Work Order Pengujian → Quotation (N—1); Work Order Pengujian 1—1/1—N LHU.

### 4.8 Sample (Transaction — starlab_lab_ops)

**Tujuan:** Melacak siklus hidup sample fisik dari penerimaan hingga pemusnahan.

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| sample_id | ID Sample | Data (unique) | Ya |
| work_order | Work Order | Link → Work Order Pengujian | Ya |
| matriks | Matriks | Select | Ya |
| tanggal_terima | Tanggal Terima | Date | Ya |
| status | Status Sample | Select (Diterima/Sedang Diuji/Divalidasi/Diarsipkan/Dimusnahkan) | Ya |
| retensi | Aksi Retensi | Select (Tahan/Bisa Dibuang) | Ya |
| tanggal_musnah | Tanggal Pemusnahan | Date | Tidak |
| catatan_kondisi | Catatan Kondisi Sample | Small Text | Tidak |

**Relationship:** Sample N—1 Work Order Pengujian; Sample 1—N Test Result.

### 4.9 Test Result (Transaction — starlab_lab_ops)

**Tujuan:** Mencatat hasil uji per parameter per sample beserta data QC.

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| sample | Sample | Link → Sample | Ya |
| work_order | Work Order (auto-fetch) | Link → Work Order Pengujian | Ya |
| parameter | Parameter | Link → Test Parameter | Ya |
| analis | Analis Pelaksana | Link → Employee | Ya |
| hasil_uji | Hasil Uji | Float | Ya |
| satuan | Satuan (auto-fetch) | Data | Ya |
| qc_detail | Data QC | Table → QC Detail (child) | Tidak |
| status | Status | Select (Draft/Diajukan Validasi/Divalidasi/Ditolak) | Ya |
| validated_by | Divalidasi Oleh | Link → Employee | Tidak |
| validated_on | Tanggal Validasi | Datetime | Tidak |
| locked | Terkunci (read-only) | Check | Tidak (auto Ya setelah Divalidasi) |
| catatan_validasi | Catatan Validasi/Penolakan | Small Text | Tidak |

**Child Table — QC Detail:** qc_type (Select: Kurva Kalibrasi/Ripitabilitas/Trueness), nilai_slope, nilai_intersep, nilai_r2, nilai_rpd_persen, nilai_trueness_persen, keterangan.

**Logic khusus:** Field `hasil_uji` dan seluruh `qc_detail` menjadi read-only otomatis ketika `status` = "Divalidasi", memenuhi kebutuhan integritas data bahwa hasil uji tidak boleh diubah setelah divalidasi Manajer Teknis.

### 4.10 LHU — Laporan Hasil Uji (Transaction — starlab_lab_ops)

**Tujuan:** Dokumen resmi hasil pengujian yang diterbitkan ke klien.

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| naming_series | Naming Series | Select (LHU-####-MM-YYYY) | Ya |
| work_order | Work Order | Link → Work Order Pengujian | Ya |
| customer | Klien (auto-fetch) | Link → Customer | Ya |
| tanggal_terbit | Tanggal Terbit | Date | Ya |
| diterbitkan_oleh | Diterbitkan Oleh | Link → Employee | Ya |
| test_result_list | Daftar Hasil Uji | Table → LHU Test Result Detail (child) | Ya |
| status | Status | Select (Draft/Issued/Revised/Superseded) | Ya |
| file_lhu | File LHU (PDF tergenerate) | Attach | Tidak |

**Relationship:** LHU N—1 Work Order Pengujian; LHU N—N Test Result (via child table); LHU 1—1 Sales Invoice.

### 4.11 Document Master (Master/Transaction — starlab_quality)

**Tujuan:** Registrasi seluruh dokumen mutu ISO/IEC 17025 menggantikan Daftar Induk Dokumen dan Distribusi.

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| document_no | No. Dokumen | Data (unique) | Ya |
| document_name | Nama Dokumen | Data | Ya |
| document_level | Level Dokumen | Select (PM/PO/IKM/DP) | Ya |
| edisi_revisi | Edisi/Revisi Saat Ini | Data | Ya |
| tanggal_efektif | Tanggal Efektif | Date | Ya |
| owner_division | Divisi Pemilik | Select | Ya |
| status | Status | Select (Aktif/Dalam Revisi/Usang) | Ya |
| file_dokumen | File Dokumen Terkini | Attach | Ya |
| distribusi | Distribusi | Table → Document Distribution (child) | Ya |
| revisi_history | Riwayat Revisi | Table → Document Revision (child, read-only) | Tidak |

**Relationship:** Document Master N—1 Employee (owner); Document Master 1—N Document Distribution; Document Master 1—N Document Revision; Test Parameter → Document Master (Link `metode_uji`).

### 4.12 Petty Cash Entry (Transaction — starlab_customizations)

**Tujuan:** UX ringan pencatatan kas kecil operasional harian dengan dukungan upload foto struk, yang di background men-generate Journal Entry ke Accounting native.

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| tanggal | Tanggal | Date | Ya |
| item | Item/Keperluan | Data | Ya |
| nominal | Nominal (Kredit) | Currency | Ya |
| bukti | Bukti (Foto/PDF) | Attach Image | Ya |
| keterangan | Keterangan | Small Text | Tidak |
| status | Status | Select (Draft/Menunggu Approval/Disetujui/Ditolak) | Ya |
| journal_entry | Journal Entry Terkait | Link → Journal Entry (read-only) | Tidak |
| disetujui_oleh | Disetujui Oleh | Link → Employee | Tidak |

**Relationship:** Petty Cash Entry 1—1 Journal Entry.

### 4.13 Inventaris — Reagen/Bahan Kimia (LIMS) vs Peralatan Kantor/Lab

Inventaris dipisah menjadi dua kategori yang berbeda karakteristik dan kebutuhan pelacakannya:

**A. Reagen/Bahan Kimia (LIMS)** — konsumsi habis pakai laboratorium, sudah tercakup sebagai Item (Stock module) dengan Reorder Level. Ditambahkan pelacakan kedaluwarsa dan batch:

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| has_batch_no | Lacak per Batch | Check (native ERPNext) | Ya (untuk item_group Reagen) |
| has_expiry_date | Lacak Tanggal Kedaluwarsa | Check (native ERPNext) | Ya |
| shelf_life_in_days | Masa Simpan (hari) | Int (native ERPNext) | Tidak |

Menggunakan fitur **Batch** bawaan ERPNext (bukan custom development) — setiap penerimaan reagen dicatat sebagai Batch baru dengan `tanggal_masuk` (manufacturing_date) dan `tanggal_kedaluwarsa` (expiry_date) miliknya sendiri, bukan field tunggal di level Item. Notifikasi mendekati/lewat kedaluwarsa memanfaatkan Scheduled Job tambahan di `starlab_lab_ops` (query Batch dengan expiry_date mendekati/terlewat, mengecualikan batch yang stoknya sudah 0).

**B. Peralatan Kantor/Lab** — DocType baru, terpisah dari reagen karena sifatnya aset tetap dengan siklus kalibrasi, bukan barang habis pakai:

| Field Name | Label | Tipe | Mandatory |
|---|---|---|---|
| nama_alat | Nama Alat | Data | Ya |
| kategori | Kategori | Select (Alat Uji Lab/Perabotan Kantor/Kendaraan/Lainnya) | Ya |
| lokasi | Lokasi/Penempatan | Data | Tidak |
| tanggal_kalibrasi_terakhir | Tanggal Kalibrasi Terakhir | Date | Tidak (wajib untuk kategori Alat Uji Lab) |
| tanggal_kalibrasi_berikutnya | Tanggal Kalibrasi Berikutnya | Date | Tidak (wajib untuk kategori Alat Uji Lab) |
| sertifikat_kalibrasi | Sertifikat Kalibrasi | Attach | Tidak |
| status_kalibrasi | Status Kalibrasi | Select (Berlaku/Mendekati Jatuh Tempo/Kedaluwarsa/Tidak Berlaku) — dihitung otomatis dari tanggal_kalibrasi_berikutnya | Ya |

Notifikasi H-30 dan H-0 terhadap `tanggal_kalibrasi_berikutnya` dikirim ke Manajer Teknis dan Manajer Mutu (relevan untuk kepatuhan ISO/IEC 17025 — instrumen yang kalibrasinya kedaluwarsa idealnya tidak dipakai untuk pengujian resmi).

**Catatan terbuka**, masih perlu klarifikasi sebelum implementasi detail: frekuensi kalibrasi standar per jenis alat (apakah seragam atau berbeda-beda per alat), apakah perlu penyedia kalibrasi eksternal dicatat sebagai vendor, dan apakah Peralatan Kantor non-lab (kendaraan, perabotan) perlu pelacakan sama sekali atau cukup pencatatan sederhana tanpa kalibrasi.

## BAB 5 — RELATIONSHIP DESIGN

```
Customer
  │
  ▼
Client Inquiry (Form A)
  │
  ▼
Kaji Ulang Permintaan/Tender (dinilai Manajer Teknis)
  │ (jika Layak/Layak dengan Catatan)
  ▼
Quotation (wajib prefilled dari Client Inquiry yang disetujui MT —
tidak ada jalur manual tanpa Form A)
  │── Link: T&C Master Template (versi berlaku saat terbit)
  │── Attach: Cover/Company Profile, Lampiran A1
  ▼
Approval Berjenjang: MT → MM → Direksi (Finance & Marketing: read-
only)
  │ (Approved / Konfirmasi Penawaran oleh Direksi)
  ▼
Cetak Quotation Final (Cover + T&C + Tabel Harga + Lampiran A1)
  │
  ▼
Work Order Pengujian
  │
  ▼
Sample (1 WO → banyak Sample)
  │
  ▼
Test Result (1 Sample → banyak Test Result, per parameter)
  │ divalidasi oleh Manajer Teknis
  ▼
LHU (agregasi Test Result tervalidasi)
  │ diterbitkan oleh Manajer Mutu
  ▼
Sales Invoice ──► Payment Entry ──► Bank Reconciliation Tool

Cabang paralel (independen dari alur pengujian):
Document Master ──(child: Document Distribution, Document Revision)
  → direferensikan oleh Test Parameter.metode_uji

Petty Cash Entry ──► auto-generate ──► Journal Entry ──► General
Ledger

Cabang eksternal (read-only, di luar Frappe):
Client Dashboard (website WordPress) ──(REST API)──► status tracking +
LHU (via ID pesanan)
```

**Catatan desain relasi kunci:** **[RESOLVED]** Client Inquiry → Quotation bersifat wajib — dikonfirmasi Product Owner bahwa seluruh Quotation, termasuk untuk client repeat, harus melalui Form A terlebih dahulu; tidak ada lagi jalur langsung. Quotation → T&C Master Template menyimpan versi spesifik yang berlaku saat terbit, agar dokumen historis tetap konsisten. Work Order Pengujian → Sample bersifat satu-ke-banyak, demikian pula Sample → Test Result. Test Result → LHU diimplementasikan via child table agar satu Test Result dapat dirujuk di LHU utama maupun LHU revisi tanpa duplikasi data.

## BAB 6 — WORKFLOW DESIGN

Seluruh workflow menggunakan Frappe Workflow Engine native (Workflow DocType + Workflow State + Workflow Action), bukan hard-code di Server Script, agar mudah disesuaikan tanpa deployment ulang.

### 6.1 Workflow — Client Inquiry (Form A)

| State | Deskripsi |
|---|---|
| Draft | Dicatat oleh Marketing saat menerima kontak awal client |
| Diajukan Kaji Ulang | Menunggu penilaian kelayakan teknis Manajer Teknis |
| Disetujui MT | Dinilai Layak/Layak dengan Catatan — memicu pembuatan Quotation Draft otomatis |
| Ditolak MT | Dinilai Tidak Layak |

**Transition & Role:** Draft → Diajukan Kaji Ulang: Action "Ajukan", Role Marketing. Diajukan Kaji Ulang → Disetujui MT/Ditolak MT: Action "Nilai Kelayakan", Role Manajer Teknis (melalui DocType Kaji Ulang Tender terkait).

### 6.2 Workflow — Quotation

| State | Deskripsi |
|---|---|
| Draft | Dibuat oleh Administrasi (wajib prefilled dari Client Inquiry yang disetujui MT) |
| Submitted | Diajukan untuk approval berjenjang |
| Menunggu Approval MT | Validasi teknis kelayakan parameter/metode |
| Menunggu Approval MM | Validasi kepatuhan regulasi acuan |
| Menunggu Approval Direksi | Persetujuan akhir dan konfirmasi penawaran |
| Approved | Siap dikirim ke klien — memicu pembuatan Work Order Pengujian otomatis |
| Perlu Revisi | Dikembalikan ke Administrasi dengan catatan alasan penolakan |
| Kedaluwarsa | Approved namun melewati 45 hari tanpa respons client |
| Cancelled | Dibatalkan setelah Approved |

**Transition & Role:**
- Draft → Submitted → Menunggu Approval MT: Action "Ajukan", Role Administrasi
- Menunggu Approval MT → Menunggu Approval MM: Action "Setujui", Role Manajer Teknis
- Menunggu Approval MM → Menunggu Approval Direksi: Action "Setujui", Role Manajer Mutu
- Menunggu Approval Direksi → Approved: Action "Setujui", Role Direksi (memicu pembuatan Work Order Pengujian otomatis)
- Setiap state approval → Perlu Revisi: Action "Tolak", Role sesuai state berjalan (mandatory field catatan penolakan)
- **[RESOLVED, UBAH ARAH]** Perlu Revisi → **Menunggu Approval MT** (bukan melanjutkan dari titik terakhir): Action "Revisi & Ajukan Ulang", Role Administrasi — **seluruh approval sebelumnya direset**, quotation wajib melalui rantai approval penuh dari awal lagi (MT → MM → Direksi). Dikonfirmasi Product Owner: perubahan pada quotation setelah sebagian disetujui membatalkan seluruh approval yang sudah ada, tidak ada mekanisme "lanjut dari titik terakhir".
- Approved → Kedaluwarsa: otomatis via Scheduled Job, saat `tanggal_kedaluwarsa` (45 hari sejak terbit) terlewati tanpa respons client
- **[BARU]** Kedaluwarsa → Approved: Action "Aktifkan Kembali", Role Administrasi — quotation dapat diaktifkan ulang (extend `tanggal_kedaluwarsa` +45 hari dari tanggal aktivasi ulang) tanpa perlu membuat quotation baru dari nol. Dikonfirmasi Product Owner.
- Approved → Cancelled: Action "Batalkan", Role Direksi atau Administrasi (dengan alasan)

Rantai persetujuan berjenjang Quotation terdiri dari tiga tahap: **Manajer Teknis → Manajer Mutu → Direksi**. Finance dan Marketing sama-sama memiliki akses baca penuh terhadap Quotation — Finance untuk kebutuhan pelaporan keuangan internal (mis. proyeksi pendapatan dari quotation yang sedang berjalan), Marketing untuk visibilitas pipeline penjualan — namun keduanya tidak memiliki peran apa pun dalam rantai persetujuan di atas. Role Marketing tetap dipertahankan di sistem (bukan dihapus) sebagai antisipasi bila perusahaan merekrut posisi Marketing di kemudian hari.

Sistem menjalankan eskalasi otomatis melalui Scheduled Job harian bila sebuah quotation berada pada satu tahap approval lebih dari 1×24 jam tanpa tindakan. **[RESOLVED]** Notifikasi eskalasi dikirim ulang ke **approver yang sama** (bukan ke atasan atau langsung ke Direksi) — dikonfirmasi Product Owner. Quotation ditandai kedaluwarsa bila melewati **45 hari** sejak tanggal terbit tanpa respons dari klien, disertai notifikasi ke Administrasi, dan dapat diaktifkan kembali (lihat transisi di atas) tanpa perlu dibuat ulang dari nol.

### 6.3 Workflow — Work Order Pengujian

| State | Deskripsi |
|---|---|
| Draft | Dibuat oleh Administrasi berdasarkan Quotation approved |
| Approved | Divalidasi kelayakan sumber daya oleh Manajer Teknis |
| In Progress | Sample diterima, pengujian berjalan |
| Completed | Seluruh Test Result terkait berstatus Divalidasi |
| Cancelled | Dibatalkan |

**Transition & Role:** Draft → Approved: Action "Setujui", Role Manajer Teknis. Approved → In Progress: Action "Mulai Pengujian", Role Laboratorium (otomatis saat Sample pertama berstatus Diterima). In Progress → Completed: otomatis via Server Script saat seluruh child WO Parameter Detail berstatus Done, atau manual oleh Manajer Teknis. Draft/Approved → Cancelled: Action "Batalkan", Role Direksi/Manajer Teknis. Completed → In Progress: Action "Buka Kembali", Role Manajer Teknis, dengan alasan wajib.

### 6.4 Workflow — Sample

| State | Deskripsi |
|---|---|
| Diterima | Sample fisik diterima laboratorium |
| Sedang Diuji | Pengujian aktif berjalan |
| Divalidasi | Seluruh Test Result terkait tervalidasi MT |
| Diarsipkan | Sample disimpan sesuai masa retensi |
| Dimusnahkan | Sample telah dibuang sesuai kebijakan retensi |

**Transition & Role:** Diterima → Sedang Diuji: Action "Mulai Uji", Role Laboratorium. Sedang Diuji → Divalidasi: otomatis ketika seluruh Test Result terkait tervalidasi. Divalidasi → Diarsipkan: Action "Arsipkan", Role Laboratorium/Manajer Teknis. Diarsipkan → Dimusnahkan: Action "Musnahkan", Role Manajer Teknis (hanya jika retensi = "Bisa Dibuang" dan tanggal musnah terlewati).

### 6.5 Workflow — Test Result

| State | Deskripsi |
|---|---|
| Draft | Diinput oleh Analis |
| Diajukan Validasi | Menunggu review Manajer Teknis |
| Divalidasi | Disetujui MT — field terkunci otomatis |
| Ditolak | Dikembalikan ke Analis dengan catatan |

**Transition & Role:** Draft → Diajukan Validasi: Action "Ajukan Validasi", Role Laboratorium. Diajukan Validasi → Divalidasi: Action "Validasi", Role Manajer Teknis (set locked = 1). Diajukan Validasi → Ditolak: Action "Tolak", Role Manajer Teknis (mandatory catatan). Ditolak → Draft: Action "Revisi", Role Laboratorium. Divalidasi → Ditolak: Action "Batalkan Validasi", hanya Manajer Teknis, dicatat di Version log.

### 6.6 Workflow — Document Control (Document Master)

| State | Deskripsi |
|---|---|
| Draft | Dokumen baru/revisi disusun oleh divisi pemilik |
| Menunggu Approval MM | Review kepatuhan mutu |
| Menunggu Approval Direksi | Persetujuan penerbitan |
| Aktif | Dokumen resmi berlaku, didistribusikan |
| Dalam Revisi | Sedang disusun ulang, versi lama tetap Aktif |
| Usang | Digantikan oleh edisi/revisi baru |

**Transition & Role:** Draft → Menunggu Approval MM: Action "Ajukan", Role divisi pemilik dokumen. Menunggu Approval MM → Menunggu Approval Direksi: Action "Setujui", Role Manajer Mutu. Menunggu Approval Direksi → Aktif: Action "Terbitkan", Role Direksi (entri baru di Document Revision, notifikasi ke seluruh Document Distribution). Aktif → Dalam Revisi: Action "Mulai Revisi", Role Manajer Mutu. Dalam Revisi → Aktif: dokumen lama otomatis menjadi Usang saat versi baru Aktif.

### 6.7 Workflow — Invoice (Sales Invoice)

| State | Deskripsi |
|---|---|
| Draft | Dibuat Administrasi dari LHU/Work Order |
| Submitted | Invoice resmi terbit (native docstatus=1) |
| Paid | Pelunasan diterima via Payment Entry reconciliation |
| Overdue | Otomatis via Scheduled Job jika melewati due date & belum lunas |
| Cancelled | Dibatalkan (native docstatus=2) |

Menggunakan mekanisme submit/cancel/amend native ERPNext — Administrasi membuat & submit, Finance melakukan reconcile Payment Entry, Direksi berwenang cancel invoice yang sudah submitted. **[RESOLVED]** Payment Terms/`due_date` Sales Invoice diset otomatis **7 hari kalender** setelah tanggal invoice terbit (Term of Payment final, dikonfirmasi Product Owner) — bukan 30 hari seperti asumsi awal di draf T&C sebelumnya. Ketentuan ini terpisah dari DP 50% di muka yang sudah diatur di T&C Quotation (Bab 4.5).

### 6.8 Workflow — Petty Cash Entry

| State | Deskripsi |
|---|---|
| Draft | Diinput oleh Administrasi |
| Menunggu Approval | Diajukan untuk disetujui |
| Disetujui | Disetujui — trigger auto-generate Journal Entry |
| Ditolak | Dikembalikan dengan catatan |

**Transition & Role:** Draft → Menunggu Approval: Action "Ajukan", Role Administrasi. Menunggu Approval → Disetujui: Action "Setujui", Role Direksi. Menunggu Approval → Ditolak: Action "Tolak", Role Direksi. Ditolak → Draft: Action "Revisi", Role Administrasi. Finance memiliki akses baca terhadap Petty Cash Entry untuk kebutuhan pelaporan, tanpa peran approval.

## BAB 7 — ROLE & PERMISSION MATRIX

Legenda: R=Read, C=Create, W=Write, D=Delete, S=Submit, X=Cancel, A=Amend, Ap=Approve.

### 7.1 Quotation

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Direksi | Ya | – | – | – | – | Ya | – | Ya (final) |
| Marketing | Ya | – | – | – | – | – | – | Tidak |
| Administrasi | Ya | Ya | Ya | Ya (Draft) | Ya | – | Ya | – |
| Finance | Ya | – | – | – | – | – | – | Tidak |
| Laboratorium | – | – | – | – | – | – | – | – |
| Manajer Teknis | Ya | – | – | – | – | – | – | Ya |
| Manajer Mutu | Ya | – | – | – | – | – | – | Ya |

Finance dan Marketing sama-sama hanya memiliki akses baca terhadap Quotation (Finance untuk pelaporan keuangan, Marketing untuk visibilitas pipeline penjualan) — tidak ada di antara keduanya yang memiliki hak approve dalam rantai persetujuan berjenjang.

### 7.2 Client Inquiry (Form A)

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Direksi | Ya | – | – | – | – | – | – | – |
| Marketing | Ya | Ya | Ya (Draft) | Ya (Draft) | – | – | – | – |
| Administrasi | Ya | Ya | Ya (Draft) | – | – | – | – | – |
| Manajer Teknis | Ya | – | – | – | – | – | – | Ya (via Kaji Ulang Tender) |
| Manajer Mutu | Ya | – | – | – | – | – | – | – |
| Finance | – | – | – | – | – | – | – | – |

### 7.3 Kaji Ulang Permintaan/Tender

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Manajer Teknis | Ya | Ya | Ya | – | – | – | – | Ya |
| Administrasi | Ya | – | – | – | – | – | – | – |
| Marketing | Ya | – | – | – | – | – | – | – |
| Direksi | Ya | – | – | – | – | – | – | – |

### 7.4 T&C Master Template

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Administrasi | Ya | Ya | Ya (level template) | – | – | – | – | – |
| Direksi | Ya | – | – | – | – | – | – | – |
| Manajer Mutu | Ya | – | – | – | – | – | – | – |
| Role lain | Ya (saat render Quotation) | – | – | – | – | – | – | – |

Tidak ada role yang dapat mengedit T&C per-dokumen quotation individual — hanya di level Master Template.

### 7.5 Work Order Pengujian

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Direksi | Ya | – | – | – | – | Ya | – | – |
| Marketing | Ya | – | – | – | – | – | – | – |
| Administrasi | Ya | Ya | Ya | Ya (Draft) | Ya | – | Ya | – |
| Finance | Ya | – | – | – | – | – | – | – |
| Laboratorium | Ya | – | Ya (child table status pengujian saja) | – | – | – | – | – |
| Manajer Teknis | Ya | – | Ya | – | Ya | Ya | Ya | Ya |
| Manajer Mutu | Ya | – | – | – | – | – | – | – |

### 7.6 Sample

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Direksi | Ya | – | – | – | – | – | – | – |
| Marketing | – | – | – | – | – | – | – | – |
| Administrasi | Ya | – | – | – | – | – | – | – |
| Finance | – | – | – | – | – | – | – | – |
| Laboratorium | Ya | Ya | Ya | – | – | – | – | – |
| Manajer Teknis | Ya | – | Ya (status arsip/musnah) | – | – | – | – | Ya |
| Manajer Mutu | Ya | – | – | – | – | – | – | – |

### 7.7 Test Result

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Direksi | Ya | – | – | – | – | – | – | – |
| Marketing | – | – | – | – | – | – | – | – |
| Administrasi | Ya | – | – | – | – | – | – | – |
| Finance | – | – | – | – | – | – | – | – |
| Laboratorium | Ya | Ya | Ya (sebelum Divalidasi) | Ya (Draft) | – | – | – | – |
| Manajer Teknis | Ya | – | Ya (buka kembali/reject) | – | – | – | – | Ya |
| Manajer Mutu | Ya | – | – | – | – | – | – | – |

### 7.8 LHU

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Direksi | Ya | – | – | – | – | Ya | – | – |
| Marketing | Ya | – | – | – | – | – | – | – |
| Administrasi | Ya | Ya | Ya (Draft) | – | – | – | – | – |
| Finance | Ya | – | – | – | – | – | – | – |
| Laboratorium | Ya | – | – | – | – | – | – | – |
| Manajer Teknis | Ya | – | – | – | – | – | – | – |
| Manajer Mutu | Ya | Ya | Ya | – | Ya | Ya | Ya | Ya (terbitkan) |

### 7.9 Sales Invoice

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Direksi | Ya | – | – | – | – | Ya | – | – |
| Marketing | Ya | – | – | – | – | – | – | – |
| Administrasi | Ya | Ya | Ya | Ya (Draft) | Ya | – | Ya | – |
| Finance | Ya | Ya | Ya | – | Ya | Ya | Ya | – |
| Laboratorium | – | – | – | – | – | – | – | – |
| Manajer Teknis | – | – | – | – | – | – | – | – |
| Manajer Mutu | – | – | – | – | – | – | – | – |

### 7.10 Petty Cash Entry

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Direksi | Ya | – | – | – | – | – | – | Ya |
| Marketing | – | – | – | – | – | – | – | – |
| Administrasi | Ya | Ya | Ya (Draft) | Ya (Draft) | – | – | – | – |
| Finance | Ya | – | – | – | – | – | – | Tidak |
| Laboratorium | – | – | – | – | – | – | – | – |
| Manajer Teknis | – | – | – | – | – | – | – | – |
| Manajer Mutu | – | – | – | – | – | – | – | – |

Approver Petty Cash Entry adalah **Direksi saja** (bukan dual approval Finance+Direksi) — keputusan ini sudah dikonfirmasi berulang kali oleh Product Owner. Finance tetap memiliki akses baca untuk pelaporan.

### 7.11 Document Master (ISO 17025)

| Role | R | C | W | D | S | X | A | Ap |
|---|---|---|---|---|---|---|---|---|
| Direksi | Ya | – | – | – | – | – | – | Ya (final) |
| Marketing | Ya (yang didistribusikan) | – | – | – | – | – | – | – |
| Administrasi | Ya (yang didistribusikan) | – | – | – | – | – | – | – |
| Finance | Ya (yang didistribusikan) | – | – | – | – | – | – | – |
| Laboratorium | Ya (yang didistribusikan) | – | – | – | – | – | – | – |
| Manajer Teknis | Ya (yang didistribusikan) | Ya (untuk IKM miliknya) | Ya | – | – | – | – | – |
| Manajer Mutu | Ya (semua) | Ya | Ya | Ya (Draft) | – | – | Ya | Ya |

Kolom "yang didistribusikan" diimplementasikan via User Permission pada Employee/Division dikombinasikan dengan Permission Level pada child table Document Distribution — bukan Role Permission murni, karena kebutuhannya adalah pembatasan tingkat baris (row-level), bukan tingkat DocType.

## BAB 8 — DASHBOARD DESIGN

**Direksi**
- Ringkasan Pendapatan vs Piutang (Sales Invoice Outstanding)
- Jumlah Work Order Aktif vs Selesai (bulan berjalan)
- Approval Pending yang menunggu tindakan Direksi (Quotation, Petty Cash, Document Control)
- Status Kas Operasional (saldo terkini)
- Funnel Client Inquiry → Quotation → Approved

**Marketing**
- Jumlah Client Inquiry (Form A) per status
- Jumlah Quotation per status (Draft/Submitted/Approved/Rejected)
- Conversion Rate Form A → Quotation → Approved
- Histori Klien (frekuensi order per klien)

**Administrasi**
- Quotation Menunggu Dibuat/Diajukan
- Client Inquiry menunggu kaji ulang Manajer Teknis
- Quotation mendekati/melewati tanggal kedaluwarsa
- Work Order Menunggu Invoice
- Reminder Approval Pending (semua dokumen yang ia ajukan)
- Petty Cash Entry — status approval

**Finance**
- Invoice Outstanding (jatuh tempo & overdue)
- Cash Flow ringkas (Rekening + Kas Kecil)
- Payment Due (7 & 30 hari ke depan)
- Ringkasan Petty Cash Entry (read-only, bukan item aksi — approval sepenuhnya di Direksi)
- Ringkasan Quotation berjalan (read-only) untuk keperluan pelaporan keuangan

**Laboratorium**
- Sample Pending (belum diuji)
- Sample Sedang Diuji
- Sample Selesai (menunggu validasi MT)
- Reminder Deadline (Target Pengujian mendekati/terlewat)
- Stok Reagen Mendekati Minimum

**Manajer Teknis**
- Test Result Menunggu Validasi
- Work Order Menunggu Approval
- Sample dengan Deadline Terlewat (SLA breach)
- Riwayat Penolakan Hasil Uji

**Manajer Mutu**
- Dokumen Menunggu Approval/Revisi
- Dokumen dengan Distribusi Belum Di-acknowledge
- LHU Draft Menunggu Diterbitkan
- Ringkasan Kepatuhan (jumlah dokumen Aktif vs Usang)

## BAB 9 — REPORT DESIGN

| Report | Tujuan | Data Source | Filter | Output |
|---|---|---|---|---|
| Funnel Form A → Quotation → Approved | Visibilitas pipeline penjualan | Client Inquiry, Kaji Ulang Tender, Quotation | Periode, Status | Grafik funnel + tabel |
| Rekap Diskon & Rush Fee | Monitoring pemberian diskon/biaya percepatan | Quotation | Periode, Customer | Tabel + Export Excel |
| Rekap Approval Stage Quotation | Identifikasi bottleneck tahap approval | Quotation (workflow log) | Periode, State | Tabel durasi rata-rata per state |
| Rekap Work Order | Monitoring seluruh WO berjalan/selesai per periode | Work Order Pengujian + WO Parameter Detail | Tanggal, Status, Customer, PJ Analis | Tabel + Export Excel/PDF |
| Status Sample Realtime | Menggantikan pengecekan manual status sample | Sample | Status, Matriks, Work Order | Tabel color-coded |
| Rekap Hasil Uji per Parameter | Analisis kinerja pengujian per parameter/analis | Test Result | Analis, Periode, Status Validasi | Tabel + grafik batang |
| Laporan Hasil Uji (LHU) Resmi | Dokumen legal untuk klien | LHU + LHU Test Result Detail | Work Order, Customer | Cetak PDF berkop surat |
| Laporan Keuangan Operasional | Menggantikan laporan kas operasional harian manual | Petty Cash Entry + Journal Entry | Periode, Kategori | Tabel + Export Excel |
| Aging Piutang | Monitoring tagihan belum lunas | Sales Invoice | Customer, Due Date, Status | Tabel aging 0-30/31-60/60+ hari |
| Rekonsiliasi Bank | Verifikasi mutasi bank vs pembukuan | Bank Transaction + Payment Entry | Periode, Akun Bank | Tabel matched/unmatched |
| Rekap Kepatuhan Dokumen Mutu | Audit internal ISO 17025 | Document Master + Document Distribution | Level Dokumen, Status, Divisi | Tabel status distribusi & acknowledgement |
| Rekap Stok Reagen & Consumable | Perencanaan pengadaan | Item + Stock Ledger Entry | Item Group, Warehouse | Tabel + alert stok kritis |
| Laporan Kinerja SLA Pengujian | Evaluasi ketepatan waktu vs target | Work Order Pengujian + Sample | Periode, Matriks | Tabel persentase keterlambatan |

## BAB 10 — NOTIFICATION DESIGN

| Notifikasi | Trigger | Penerima | Kanal |
|---|---|---|---|
| Client Inquiry Menunggu Kaji Ulang | Client Inquiry berpindah ke "Diajukan Kaji Ulang" | Manajer Teknis | Frappe Notification + WhatsApp |
| Client Inquiry Disetujui/Ditolak | Kaji Ulang Tender diselesaikan | Marketing yang membuat Form A | Frappe Notification |
| Approval Pending Quotation | Quotation berpindah ke state "Menunggu Approval [MT/MM/Direksi]" | Role terkait sesuai state | Frappe Notification + Email + WhatsApp |
| Eskalasi SLA Approval Quotation | Quotation berada pada satu state approval lebih dari 1×24 jam | Approver terkait | Frappe Notification + Email |
| Quotation Kedaluwarsa | Tanggal kedaluwarsa terlewati, status belum direspons client | Administrasi | Frappe Notification + Email |
| Sample Deadline Mendekat | Target pengujian jatuh H-2, status belum Done | Laboratorium & Manajer Teknis | Frappe Notification + WhatsApp |
| Sample Deadline Terlewat | Target pengujian lewat, status belum Done | Manajer Teknis & Direksi | Frappe Notification + Email |
| Invoice Due | Due date jatuh H-3, outstanding > 0 | Finance & Administrasi | Frappe Notification + Email |
| Invoice Overdue | Due date lewat, outstanding > 0 | Finance & Direksi | Frappe Notification + Email + WhatsApp |
| Stock Minimum | Reorder Level tercapai | Laboratorium & Administrasi | Frappe Notification + WhatsApp |
| Document Revision Terbit | Document Master berpindah ke "Aktif" | Seluruh divisi pada Document Distribution | Frappe Notification + Email |
| Test Result Ditolak | Test Result berpindah ke "Ditolak" | Analis pembuat | Frappe Notification |
| Sample Retensi Jatuh Tempo | Tanggal pemusnahan tercapai | Laboratorium & Manajer Teknis | Frappe Notification |

Notifikasi berbasis perubahan status menggunakan Frappe Notification DocType (Document Event: Value Change/Workflow). Notifikasi berbasis waktu (deadline, due date, retensi, eskalasi SLA) menggunakan Notification tipe "Alert" dikombinasikan dengan Scheduled Job harian. Pengiriman WhatsApp diteruskan lewat Server Script di `starlab_integrations`.

## BAB 11 — INTEGRATION DESIGN

| Integrasi | Kebutuhan | Pendekatan Teknis |
|---|---|---|
| WhatsApp | Meneruskan notifikasi ke kanal kerja dominan staf | Server Script di `starlab_integrations` memanggil REST API WhatsApp Business API/gateway pihak ketiga; nomor tujuan dari field `mobile_no` Employee/Contact |
| Client Dashboard API | Menyediakan status tracking + tautan unduh LHU berdasarkan ID/nomor pesanan, **tanpa login** | REST endpoint whitelisted (`allow_guest=True`) di `starlab_integrations`, menerima nomor Quotation/Work Order Pengujian, mengembalikan status pekerjaan + tautan unduh LHU (tanpa data harga/finansial apa pun). Dilengkapi rate-limiting agar nomor pesanan tidak bisa ditebak-tebak dari luar |
| Client Dashboard — Halaman Publik | Antarmuka bagi klien untuk mengecek status | Halaman www di `starlab_integrations` (form input nomor pesanan + tombol cek), dapat diakses tanpa login, memanggil endpoint di atas via fetch. Website SAI (WordPress) cukup menambahkan satu tautan/menu yang mengarah ke halaman ini — tidak perlu integrasi kode di sisi WordPress. Portal login-based (`/status-klien`, berbasis Portal User) tetap tersedia sebagai kanal alternatif bagi klien yang sudah punya akun, namun bukan kanal utama |
| Email | Notifikasi formal & pengiriman dokumen (Quotation, Invoice, LHU) ke klien | Native Frappe Email Queue + Email Template Builder, terhubung ke SMTP perusahaan |
| PDF Generation | Cetak Quotation, LHU, Invoice dengan kop surat resmi | Native Print Format Builder (wkhtmltopdf), termasuk penggabungan komponen Quotation (Cover, T&C, tabel harga, Lampiran A1) menjadi satu dokumen saat cetak |
| Excel Import | Migrasi data historis dari Google Drive/Excel ke sistem baru | Native Data Import Tool dengan template mapping per DocType; data QC kompleks memakai skrip migrasi Python custom |
| Bank Reconciliation | Rekonsiliasi rekening koran terhadap pembukuan | Native Bank Statement Import → Bank Reconciliation Tool |
| Lokalisasi Bahasa | Label UI Bahasa Indonesia, nama teknis tetap Bahasa Inggris | Fitur Translation bawaan Frappe, teks dikelola melalui mekanisme translation string standar |
| **[BARU]** Integrasi Accurate (software akuntansi) | Data quotation/keuangan yang sudah Approved perlu masuk ke sistem akuntansi Accurate yang dipakai Finance | **Belum didesain** — cakupan teknis masih bergantung jawaban dari perusahaan: apakah dibutuhkan integrasi API otomatis (real-time sync ke Accurate), atau cukup proses ekspor/input manual berkala oleh Finance seperti kebiasaan saat ini. Jangan mulai membangun integrasi apa pun sebelum cakupan ini dikonfirmasi — potensi effort-nya jauh berbeda antara kedua opsi |

## BAB 12 — FRAPPE DEVELOPMENT ROADMAP

Roadmap ini disusun dalam Sprint teknis dua mingguan, mengikuti prinsip dependency-first (setiap sprint membangun fondasi untuk sprint berikutnya) dan quick-win-first (menyelesaikan pain point tertinggi lebih dulu) sebelum masuk ke pengembangan custom yang lebih kompleks.

**Sprint 1 — Setup & Master Data**
- Setup instance Frappe/ERPNext (bench, site, apps install)
- Setup Company, Chart of Account, Fiscal Year
- Master Data: Customer, Employee (7 role mapping), Item (reagen/consumable)
- Custom App `starlab_lab_ops` — DocType Test Parameter (master data)
- Alasan urutan: Seluruh proses transaksi bergantung pada master data ini; tanpa Customer/Employee/Test Parameter, tidak ada DocType transaksi lain yang bisa dibangun.

**Sprint 2 — Quotation & Approval**
- Custom App `starlab_customizations` — Custom Field & child table pada Quotation
- Workflow Design Quotation dikonfigurasi di Workflow Builder
- Role Permission dasar untuk Quotation
- Alasan urutan: Quotation adalah pain point tertinggi dan hanya butuh konfigurasi ringan di atas DocType native — quick win tercepat untuk membangun kepercayaan pengguna terhadap sistem baru.

**Sprint 3 — Work Order Pengujian**
- Custom App `starlab_lab_ops` — DocType Work Order Pengujian + child table WO Parameter Detail
- Workflow Design Work Order Pengujian dikonfigurasi
- Role Permission Work Order
- Alasan urutan: Bergantung pada Test Parameter (Sprint 1) dan Quotation approved (Sprint 2) sebagai sumber data; merupakan pintu masuk ke seluruh proses laboratorium.

**Sprint 4 — Sample Tracking**
- Custom App `starlab_lab_ops` — DocType Sample
- Workflow Design Sample dikonfigurasi
- Dashboard Laboratorium versi awal (Sample Pending/Sedang Diuji)
- Alasan urutan: Bergantung langsung pada Work Order Pengujian (Sprint 3); merupakan unit kerja harian staf lab sehingga perlu stabil sebelum modul QC dibangun di atasnya.

**Sprint 5 — Pra-Quotation & Perluasan Master Data**
- Custom App `starlab_customizations` — DocType Client Inquiry (Form A), Kaji Ulang Permintaan/Tender, T&C Master Template
- Perluasan Custom Field & Child Table pada Quotation: Discount (%), Biaya Kirim, Rush Fee, referensi Client Inquiry, referensi T&C Master Template, Cover/Company Profile, Lampiran A1, histori LHU klien, tanggal kedaluwarsa otomatis
- Perluasan Custom Field Customer: kategori pelanggan
- Workflow Client Inquiry dan penyesuaian Workflow Quotation (tiga tahap approval: MT, MM, Direksi — Finance dan Marketing bersifat read-only, tidak masuk rantai approval)
- Scheduled Job: eskalasi SLA approval 1×24 jam, auto-expiry quotation 30 hari
- Role Permission untuk Client Inquiry, Kaji Ulang Tender, T&C Master Template, dan pembaruan Role Permission Quotation
- Konfigurasi Print Format gabungan (Cover, T&C, tabel harga, Lampiran A1) dan tombol cetak satu klik
- Aktivasi fitur Translation untuk lokalisasi label UI Bahasa Indonesia
- Alasan urutan: Melengkapi modul Quotation & Master Data yang sudah berjalan sejak Sprint 1–2 dengan alur pra-quotation dan kelengkapan dokumen quotation, sebelum tim beralih ke pengembangan modul Quality Control yang lebih kompleks.

**Sprint 6 — Quality Control (Test Result) & LHU**
- Custom App `starlab_lab_ops` — DocType Test Result (+ child table QC Detail, Server Script kalkulasi & lock logic)
- DocType LHU + Print Format resmi
- Workflow Design Test Result dikonfigurasi
- Alasan urutan: Bergantung pada Sample (Sprint 4); merupakan bagian paling kompleks secara logika (kalkulasi QC, status lock) sehingga dijadwalkan setelah fondasi data lab (Work Order, Sample) stabil.

**Sprint 7 — Invoice, Petty Cash & Bank Reconciliation**
- Custom Field Sales Invoice (Link Work Order Pengujian/LHU)
- Custom App `starlab_customizations` — DocType Petty Cash Entry + Server Script auto-generate Journal Entry
- Workflow Design Invoice & Petty Cash Entry
- Setup Bank Reconciliation Tool + Bank Statement Import
- Alasan urutan: Menutup siklus transaksi dari pengujian ke penagihan; secara teknis independen dari Sprint 3–6 sehingga bisa paralel, namun ditempatkan setelah LHU (Sprint 6) karena Invoice idealnya merujuk ke LHU sebagai dasar penagihan.

**Sprint 8 — Document Control (ISO 17025)**
- Custom App `starlab_quality` — DocType Document Master, Document Distribution, Document Revision
- Workflow Design Document Control dikonfigurasi
- Role Permission Document Control (row-level via User Permission)
- Alasan urutan: Secara fungsional independen dari alur transaksi lab, sehingga aman dikerjakan setelah inti operasional stabil; namun harus selesai sebelum go-live penuh karena menyangkut kepatuhan ISO/IEC 17025.

**Sprint 9 — Dashboard, Report & Notification**
- Seluruh Dashboard per role (Bab 8)
- Seluruh Report (Bab 9)
- Notification Framework + Scheduled Job (Bab 10)
- Alasan urutan: Dashboard, Report, dan Notification mengonsumsi data dari seluruh DocType yang dibangun Sprint 1–8 — baru bisa dibangun dengan benar setelah struktur data final tersedia.

**Sprint 10 — Integrasi WhatsApp & Client Dashboard**
- Custom App `starlab_integrations` — WhatsApp Gateway
- REST API Client Dashboard berbasis nomor pesanan tanpa login (Bab 11), lengkap dengan rate-limiting
- Halaman www publik untuk cek status + unduh LHU pakai nomor pesanan
- Website SAI (WordPress) cukup ditambahkan satu tautan/menu ke halaman ini — jauh lebih ringan dibanding rencana awal yang membutuhkan integrasi kode di sisi WordPress
- Alasan urutan: Bersifat penyempurnaan pengalaman, tidak menghambat operasional inti jika ditunda; membutuhkan seluruh Notification Framework (Sprint 9) sudah berjalan sebagai basis trigger.

**Sprint 11 — Migrasi Data, UAT & Go-Live**
- Migrasi data historis (Data Import Tool + skrip Python custom untuk data QC kompleks)
- User Acceptance Testing per role, termasuk alur Client Inquiry → Kaji Ulang → Quotation dan workflow approval tiga tahap
- Training bertahap agar tidak mengganggu kegiatan rutin operasional
- Go-live bertahap: Sprint 2, 3, 5 (Quotation, Work Order, Pra-Quotation) lebih dulu → Sprint 4, 6 (Sample, QC) → sisanya
- Alasan urutan: Migrasi dan UAT dilakukan setelah seluruh modul fungsional (Sprint 1–10) selesai dibangun dan diuji unit, agar data yang dimigrasikan langsung tervalidasi terhadap struktur DocType final — menghindari migrasi ulang.

**Sprint 12 — Penyesuaian Quotation Berdasarkan Keputusan Product Owner**
- Logika revisi: ubah dari "lanjut dari titik terakhir" menjadi reset penuh ke Menunggu Approval MT saat quotation direvisi setelah sebagian disetujui
- Expiry Quotation: 30 → 45 hari, tambah state "Kedaluwarsa" + action "Aktifkan Kembali" (reaktivasi tanpa buat baru)
- Eskalasi SLA: pastikan target notifikasi adalah approver yang sama (bukan atasan/Direksi)
- Validasi: field `client_inquiry` di Quotation menjadi wajib — hapus/nonaktifkan jalur pembuatan Quotation tanpa Form A
- Field `tingkat_percepatan` (Select) pada Quotation dengan 2 tier terkonfirmasi (5 Hari Kerja +100%, 7 Hari Kerja +80%) + opsi "Lainnya" manual
- Konsolidasi field `jenis_industri` dan `kategori_pelanggan` di Customer menjadi satu field, migrasi data bila diperlukan
- Update konten T&C Master Template: masa berlaku 45 hari, pelunasan 7 hari kalender setelah invoice terbit
- Payment Terms Sales Invoice: due date = tanggal invoice + 7 hari
- Tambah test untuk setiap logika di atas
- Alasan urutan: Seluruh item adalah koreksi atas asumsi yang sudah terlanjur dibangun di Sprint 5, berdasarkan jawaban konkret Product Owner yang baru diterima — diprioritaskan sebelum fitur baru (Sprint 13) karena memperbaiki perilaku yang sudah berjalan dan berpotensi dipakai user.

**Sprint 13 — Inventaris Reagen & Peralatan (LIMS vs Kantor)**
- Aktivasi Batch + Expiry Date native ERPNext untuk Item kategori Reagen
- Custom App `starlab_lab_ops` — DocType Peralatan Kantor/Lab + kalkulasi status kalibrasi otomatis
- Scheduled Job notifikasi kedaluwarsa reagen (per Batch) dan jatuh tempo kalibrasi alat (H-30, H-0)
- Alasan urutan: Requirement yang baru dikonfirmasi setelah Sprint 1–11 berjalan; secara teknis independen dari modul lain sehingga aman dikerjakan kapan saja tanpa mengganggu modul yang sudah stabil.

**Sprint 14 — Integrasi Accurate (menunggu klarifikasi cakupan)**
- Status: **belum dapat dimulai** — cakupan teknis (integrasi API otomatis vs proses manual) masih menunggu jawaban dari perusahaan (lihat Bab 11)
- Setelah cakupan jelas: bila otomatis, rancang REST API/webhook sinkronisasi ke Accurate di `starlab_integrations`; bila manual, cukup sediakan fitur export data quotation/invoice dalam format yang memudahkan input manual Finance (mis. Excel export terstruktur)
- Alasan urutan: Ditempatkan paling akhir karena effort-nya bisa sangat berbeda tergantung jawaban, dan tidak menghambat modul lain jika ditunda.

## BAB 13 — CATATAN IMPLEMENTASI LANJUTAN

Beberapa hal berikut masih memerlukan konfirmasi lebih lanjut dari stakeholder terkait sebelum atau selama pengerjaan berlangsung:

1. Kepemilikan akses admin wp-admin website SAI — untuk keperluan menambah tautan/menu ke halaman Client Dashboard (hanya perlu 1 tautan, bukan akses hosting/tema penuh).
2. Detail teknis Inventaris Peralatan (Bab 4.13): frekuensi kalibrasi standar per jenis alat, kebutuhan pencatatan vendor kalibrasi eksternal, dan cakupan pelacakan untuk Peralatan Kantor non-lab.
3. Cakupan teknis integrasi Accurate (Bab 11, Sprint 14): apakah dibutuhkan sinkronisasi otomatis (API) atau cukup proses ekspor/input manual berkala oleh Finance.
4. Tier rush fee di luar 5 hari (+100%) dan 7 hari (+80%) — belum ada aturan baku bila client minta percepatan ke jumlah hari lain.

**Sudah terjawab dan tidak perlu diklarifikasi ulang:**
- Peran Finance dan Marketing pada Quotation — keduanya read-only, bukan approver. Rantai approval final: MT → MM → Direksi.
- Approver Petty Cash Entry — Direksi saja, bukan dual approval dengan Finance.
- Mekanisme keamanan Client Dashboard — berbasis nomor pesanan tanpa login.
- Status role Marketing di organisasi — role tetap dipertahankan di sistem, tidak dihapus, tidak dijadikan rangkap fungsi role lain.
- Target eskalasi SLA — notifikasi ulang ke approver yang sama.
- Logika revisi quotation — approval sebelumnya direset penuh, wajib ulang dari MT.
- Masa berlaku quotation — 45 hari, dapat diaktifkan kembali (bukan wajib buat baru).
- Form A — wajib untuk seluruh Quotation, tidak ada jalur langsung.
- Rush fee — 2 tier terkonfirmasi (5 hari/+100%, 7 hari/+80%).
- Override Kaji Ulang Tender "Tidak Layak" — keputusan final, tidak ada eskalasi.
- Modul penanganan Lampiran A1 terisi — tetap di Administrasi/modul Quotation.
- Pencatatan komunikasi informal sebelum Form A — tetap informal, dicatat di field catatan bila ada tambahan relevan.
- Term of Payment — pelunasan invoice maksimal 7 hari kalender setelah invoice terbit (terpisah dari DP 50% di muka).
- Kesamaan field "jenis industri" dan "kategori pelanggan" — sama, sudah dikonsolidasi jadi satu field.
- Penentu kewajaran diskon sebelum ke Direksi — Administrasi.
- Makna istilah "Accurate" — merujuk pada sistem akuntansi Accurate yang dipakai Finance (detail cakupan integrasi masih poin #3 di atas).

---

*Dokumen ini disusun berdasarkan Business Requirement Analysis (BRA) ERP SAI dan Product Requirement Document (PRD) Quotation & Master Data SAI v8, sebagai rujukan teknis siap-implementasi bagi tim developer Frappe Framework.*
