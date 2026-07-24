# PRD — Modul Quotation & Master Data

## ERP PT Starlab Analitik Indonesia (SAI) — Frappe/ERPNext

**Status:** Draft v6 — Revisi dari v5, menambahkan penguatan bukti approver Finance dari cross-check data gforms, dan rekap konsolidasi Open Questions yang masih perlu ditindaklanjuti ke stakeholder terkait
**Basis dokumen:** BRA ERP SAI, TSD ERP SAI, Project Plan ERP SAI, PRD v1-v4, Quotation PT Yanmar Indonesia (Quo-SAI/V/2026/075, versi lengkap 6 halaman) & Lampiran A1, Quotation PT Cipta Himayata (Quo-SAI/V/2026/076, dokumen rincian internal), LHU 023/LHU/SAI/III/2026, form respons pengumpulan data awal ERP (6 responden divisi), repo `starlab_lab_ops` & `web-starlab`, diskusi lanjutan sesi berjalan
**Modul terkait berikutnya:** Work Order Pengujian, Sample Tracking, Hasil Uji/LHU (PRD terpisah, dependency dari modul ini)

> **Catatan untuk AI Agent:** PRD ini adalah dokumen acuan utama implementasi modul Quotation & Master Data (termasuk pra-quotation) pada proyek ERP PT Starlab Analitik Indonesia (SAI) berbasis Frappe Framework/ERPNext. Dokumen sumber tambahan (BRA, TSD, Project Plan ERP SAI) ada di folder `/docs/` pada root project ini — baca dokumen tersebut untuk konteks lebih lengkap bila diperlukan. Ikuti instruksi berikut saat men-generate atau mengubah kode berdasarkan PRD ini:
>
> 1. Nama teknis DocType, field, dan API tetap dalam Bahasa Inggris; label yang tampil ke user (label field, judul menu, pesan) dalam Bahasa Indonesia — lihat Bagian 5.8.
> 2. Jangan mengubah urutan approval (Bagian 5.4) atau logika revisi di luar yang sudah didefinisikan tanpa konfirmasi eksplisit dari Product Owner — masih berstatus asumsi kerja (lihat Bagian 10).
> 3. Setiap item di Bagian 10 (Open Questions) masih terbuka — jangan diam-diam mengambil keputusan sendiri saat implementasi; beri tanda `// TODO: lihat PRD Bagian 10` di kode terkait, atau tanyakan balik ke user.
> 4. Dokumen ini adalah PRD fondasi/utama untuk sisi penjualan (pra-quotation → quotation → trigger Work Order) — modul lanjutan (Work Order Pengujian, Sample Tracking, Hasil Uji, LHU) punya PRD terpisah yang mereferensikan modul ini; jangan menggabungkan requirement modul lain ke sini, kecuali kebutuhan tampilan (view) yang secara eksplisit dijelaskan sebagai bagian siklus quotation (lihat Bagian 5.7).
> 5. **[BARU v5]** Implementasi modul ini ditempatkan di custom app **`starlab_customizations`** (bukan `starlab_lab_ops`/`starlab_integrations`/`starlab_quality`) — lihat Bagian 7 untuk konteks struktur repo.
>
> Beberapa keputusan approval di dokumen ini adalah **asumsi kerja** mengikuti rekomendasi BRA, karena Fase 0 (resolusi konflik BRA Bagian 8 + sign-off Direksi, per Project Plan) belum selesai.

---

## Changelog v5 → v6

| # | Perubahan | Alasan |
|---|---|---|
| 1 | **[PENGUAT BUKTI]** Approver **Finance** dikonfirmasi ulang **tetap masuk** rantai approval quotation (Bagian 5.4, Open Q#3) — sempat dipertanyakan ulang berdasarkan pembacaan catatan tangan yang menyebut "Akuntan" tanpa kata "Finance" eksplisit, tapi ternyata di data gforms respondennya sendiri (Dani Ramdani) menuliskan jabatannya sebagai **"Finance / Akuntan"** (istilah yang dipakai bergantian secara internal, bukan 2 role berbeda). Astri (Administrasi) juga eksplisit menyebut "Finance" sebagai salah satu approver-nya. Tidak ada perubahan pada urutan approval Bagian 5.4 — ini murni penguatan bukti, bukan koreksi | Cross-check ulang antara catatan tangan PO dan data gforms atas permintaan tim |
| 2 | **[BARU]** Rekap konsolidasi status seluruh Open Questions ditambahkan sebagai referensi cepat — lihat ringkasan di akhir Bagian 10 | Memudahkan tim menindaklanjuti item yang masih perlu klarifikasi ke stakeholder terkait |

---

## Changelog v4 → v5

| # | Perubahan | Alasan |
|---|---|---|
| 1 | **[KOREKSI]** Peran "Marketing" sebagai role/pegawai terpisah dikoreksi di seluruh dokumen (Bagian 3, 5.4) — Marketing **bukan** role tersendiri, dijalankan rangkap oleh Administrasi/MM/Direksi dengan **All Access** | Dikonfirmasi silang dari form respons pengumpulan data awal ERP — tidak ada satu pun dari 6 responden yang menjabat "Marketing" sebagai divisi berdiri sendiri; approver list yang disebut Administrasi (Astri) juga tidak menyertakan "Marketing" sebagai entitas terpisah |
| 2 | **[BARU]** Struktur cetak Quotation final dirinci: **4 komponen terpisah** yang di-*merge* — (a) Cover/Company Profile statis 3 halaman, (b) Syarat & Ketentuan statis 1 halaman, (c) tabel harga dinamis per-quotation, (d) Lampiran A1 (blank, dikirim kosong ke client) — lihat Bagian 5.3 & 5.6 | Ditemukan dari dokumen Quo 075 versi lengkap (6 halaman): urutan halaman & header masing-masing terlihat jelas sebagai 4 dokumen berbeda yang digabung, bukan 1 dokumen tunggal |
| 3 | **[KOREKSI ARAH]** Open Question Lampiran A1 (dulu #12) **direframe total** — bukan soal "field masuk Master Data Customer atau lampiran per-quotation", tapi soal **alur input balik dari client**: Lampiran A1 dikirim **kosong** ke client sebagai bagian quotation, **diisi oleh client** setelah PO disetujui, dan hasil isiannya jadi syarat konfirmasi jadwal sampling (T&C poin 4). Pertanyaan yang relevan sekarang: apakah alur input-balik ini bagian dari modul Quotation, atau sudah masuk ranah Work Order/Sample Tracking (Bagian 10) | Dikonfirmasi eksplisit oleh Product Owner setelah verifikasi isi dokumen Quo 075 asli — asumsi awal PRD v3/v4 soal Lampiran A1 diisi Administrasi ternyata keliru |
| 4 | **[BARU]** Field **Discount (%)** dan **Biaya Kirim** ditambahkan sebagai field terstruktur di ringkasan Quotation (Bagian 5.3), sejajar dengan PPN | Ditemukan di tabel ringkasan harga Quo 075: urutan `Sub Total → Discount 5% → DPP → PPN 11% → B. Kirim → Total Invoice` — field ini belum tercatat di PRD v1-v4 |
| 5 | **[REVISI CONFIDENCE, masih terbuka]** Field "Accurate" — muncul hipotesis ke-3: kemungkinan bukan field data sama sekali, melainkan **catatan urutan proses kerja** ("pastikan data quotation sudah akurat/final, baru lampirkan cover dkk"). Confidence antara 3 hipotesis (tagline "Akurat" / integrasi software Accurate / catatan urutan proses) **belum bisa diputuskan dari dokumen manapun** — disepakati untuk **ditunda/di-deprioritaskan**, tidak diklarifikasi dalam waktu dekat | Disepakati dengan Product Owner: klarifikasi butuh komunikasi langsung (bukan re-interpretasi dokumen/foto), dan tidak mendesak untuk sprint saat ini |
| 6 | **[KLARIFIKASI]** Kejanggalan dugaan sebelumnya soal Quo 076 "tidak lengkap" (tanpa cover/T&C/Lampiran A1) **bukan inkonsistensi** — Quo 076 adalah dokumen rincian isi/breakdown internal, bukan dokumen final yang dikirim ke client (yang lengkap dan mengikuti format 4 komponen di atas adalah Quo 075) | Dikonfirmasi Product Owner |
| 7 | **[BARU]** Field **"Kategori Pelanggan"** (checkbox: Perusahaan/Individu-Perorangan/Institusi Pemerintah/Universitas-Sekolah/Lain-lain) ditemukan di dokumen LHU — kemungkinan besar ini yang dimaksud sebagai "jenis industri" pada perluasan DocType Customer di Bagian 5.2, tapi **belum dikonfirmasi** apakah sama persis atau field terpisah (Bagian 10) | Ditemukan di header LHU 023 |
| 8 | **[BARU]** Keputusan strategi repository: hanya custom app (`starlab_customizations`, `starlab_integrations`, `starlab_lab_ops`, `starlab_quality`) yang di-*version control* di GitHub perusahaan; source code core Frappe/ERPNext **tidak** di-push (ditarik via `bench get-app` mengikuti praktik standar ekosistem Frappe). Modul Quotation & Master Data ini ditetapkan masuk ke app **`starlab_customizations`** | Keputusan teknis tim, dikonfirmasi tidak ada kebutuhan khusus (air-gapped deployment, compliance internal) yang mengharuskan vendoring penuh |
| 9 | **[BARU] Blocker baru untuk Bagian 5.7 (Client Dashboard):** repo `web-starlab` yang tersedia ternyata merupakan **hasil static export/mirror** dari situs WordPress live (`starlabanaltikind.com`), bukan source code yang di-deploy langsung — sehingga penambahan halaman Client Dashboard butuh **akses WP Admin/hosting panel situs live**, yang statusnya belum jelas dimiliki siapa. Ditambahkan sebagai dependency baru di Bagian 7 dan Open Question baru di Bagian 10 | Ditemukan saat inspeksi struktur repo `web-starlab` (isinya wp-content/wp-includes/sitemap.xml hasil crawl statis, 1 commit, tanpa wp-config.php/database) |

---

## Changelog v1 → v2

Perubahan ini berdasarkan requirement tambahan dari diskusi stakeholder (belum tertulis di BRA/TSD asli), digabungkan ke PRD ini sesuai arahan Product Owner:

| # | Perubahan | Alasan |
|---|---|---|
| 1 | Tambah alur **Pra-Quotation**: Form A (permintaan awal client via telepon/WA) → Form Kaji Ulang Permintaan/Tender (review MT) → baru masuk Quotation Draft (Bagian 5.1 baru) | Mengisi gap BRA Bagian 2 & PRD v1 Non-Goal #3 ("belum ada input dari Marketing") — sekarang sudah ada alurnya |
| 2 | Tambah field pada Quotation: **biaya percepatan** (hari + %), **cover/proposal**, referensi histori LHU/PT klien, **konfirmasi faktur revisi** (Bagian 5.3) | Detail tambahan dari alur bisnis riil quotation SAI |
| 3 | Field **"Accurate"** pada Quotation ditandai **belum jelas maknanya** — kemungkinan integrasi software akuntansi Accurate Online, masih dikonfirmasi ke tim internal (Bagian 10, Open Question baru) | Belum ada kepastian dari Product Owner saat PRD ini disusun |
| 4 | Tambah **Client Dashboard** (Bagian 5.7, baru) — portal ringan di website SAI, hanya tracking status + download LHU via ID pesanan, **tanpa approval** | Membatalkan sebagian Non-Goal v1 "Tidak ada Client Portal" — sekarang portal *read-only* masuk scope, tapi portal transaksional/approval tetap Out of Scope |
| 5 | Tegaskan kebutuhan **cetak langsung (one-click print)**, bukan sekadar export PDF (Bagian 5.6) | Permintaan eksplisit dari Administrasi |
| 6 | Konfirmasi pembagian kerja: **Quotation dikerjakan Administrasi**, **LHU dikerjakan Manajer Mutu** — tidak berubah dari v1/TSD, dicatat ulang di sini sebagai penegasan | Validasi silang, tidak ada perubahan substansi |
| 7 | Modul **Inventaris (LIMS vs Kantor)** — dicatat sebagai catatan silang tapi **TIDAK dimasukkan ke PRD ini**; direkomendasikan jadi PRD terpisah (lihat Bagian 8, Out of Scope) | Di luar cakupan domain Quotation & Master Data; lebih cocok di modul Inventory/Asset |
| 8 | Non-Goal "Tidak mencakup proses CRM/akuisisi klien sebelum quotation" **direvisi** — sebagian sudah in-scope (Form A sebagai pencatatan inquiry), tapi CRM penuh (leads pipeline, campaign tracking) tetap Out of Scope | Batas scope perlu tetap jelas agar tidak melebar jadi modul CRM |

---

## Changelog v2 → v3

Perubahan ini berdasarkan verifikasi silang terhadap dokumen quotation riil (PT Yanmar Indonesia) dan contoh LHU — beberapa interpretasi di v2 **dikoreksi** karena ternyata meleset dari maksud aslinya:

| # | Perubahan | Alasan |
|---|---|---|
| 1 | **[KOREKSI]** "Cover/Proposal" diperjelas: ini adalah **company profile/proposal marketing statis** (identitas perusahaan, ruang lingkup layanan, akreditasi, galeri kegiatan) yang sama untuk semua quotation — **bukan** konten dinamis yang diketik ulang per-quotation (Bagian 5.3) | Terlihat jelas dari dokumen company profile "2026 — Proposal Penawaran — All Industry One Solutions" yang formatnya generik/branding, bukan spesifik per-klien |
| 2 | **[KOREKSI]** "Konfirmasi Faktur Revisi" **bukan** field tracking approval internal seperti ditulis di v2 — ini adalah **klausul Syarat & Ketentuan** yang tercetak di body quotation (batas waktu client boleh minta revisi faktur pajak: maksimal tanggal 10 bulan berikutnya) (Bagian 5.3) | Ditemukan eksplisit di poin 9 Syarat & Ketentuan quotation PT Yanmar |
| 3 | **[BARU]** Tambah **Syarat & Ketentuan (T&C)** sebagai blok requirement formal — **template statis/tetap**, otomatis tercetak di semua quotation, **tidak bisa diedit Administrasi** (keputusan sudah dikonfirmasi Product Owner) (Bagian 5.3 & 5.9 baru) | Ditemukan 12 poin T&C standar (masa berlaku, mekanisme PO, jadwal sampling, proses LHU, dokumen penagihan, syarat pembayaran, faktur pajak/PPh23, retensi sampel, pembatalan) di quotation riil — belum tercatat sama sekali di v1/v2 |
| 4 | **[REVISI CONFIDENCE]** Field **"Accurate"** — kemungkinan besar salah dengar/typo dari tagline **"Akurat"** (dipakai di branding: *"Akurat, Konsisten, dan Terpercaya"*), bukan integrasi software Accurate Online. Confidence naik tapi **belum final** — tetap di Open Questions (Bagian 10) | Ditemukan tagline "Akurat" berulang di company profile |
| 5 | **[BARU]** Lampiran A1 — Form Identitas Pelanggan (identitas perusahaan + NPWP, PIC Pendaftaran, PIC Keuangan) dicatat sebagai kebutuhan baru, **statusnya masih Open Question** (masuk Master Data Customer atau lampiran terpisah per quotation) — lihat Bagian 10 | Ditemukan sebagai lampiran wajib di quotation PT Yanmar, belum ada padanannya di PRD v1/v2 |
| 6 | **[BARU]** Ditegaskan: komunikasi Marketing ↔ Client sebelum Form A (telepon/WA awal) **tetap privat, di luar sistem** — tidak masuk Client Dashboard maupun dicatat sistem. Status **final pending konfirmasi Dirut** (Bagian 10) | Arahan eksplisit dari Product Owner, tapi belum sign-off resmi |
| 7 | Format auto-numbering `Quo-SAI/[bulan romawi]/[tahun]/[no urut]` makin diperkuat — dua contoh riil (075 & 076, sama-sama Mei/V/2026) konsisten dengan format ini, tapi tetap disarankan konfirmasi resmi ke Administrasi sebelum dikunci (tidak diubah statusnya di Open Questions, hanya makin kuat evidence-nya) | Cross-check 2 dokumen quotation berbeda klien |

---

## Changelog v3 → v4

| # | Perubahan | Alasan |
|---|---|---|
| 1 | **[KOREKSI ARAH]** Field "Accurate" — dari catatan tulisan tangan asli, "accurate" tercatat sejajar/terpisah dari "Cover", sama-sama komponen pembentuk Quotation → confidence bergeser lagi ke arah **kemungkinan integrasi software Accurate**, membalikkan hipotesis v3 (tagline "Akurat"). Tetap belum final (Bagian 5.3 & 10) | Verifikasi langsung ke sumber asli (catatan tulisan tangan Product Owner) |
| 2 | **[RESOLVED]** Kewenangan mengubah Master Template Syarat & Ketentuan → **Administrasi**, karena Administrasi adalah pemilik proses quotation end-to-end. Dipindah dari Open Questions ke keputusan final (Bagian 5.3 & 10) | Konfirmasi langsung dari Product Owner |
| 3 | **[BARU]** Open Question soal **Term of Payment (TOP) default** — indikasi 7 hari, ditandai tanda tanya, eksplisit butuh konfirmasi Direktur (Dio) (Bagian 10) | Ditemukan di catatan tulisan tangan Product Owner |

---

## 1. Overview / Problem Statement

SAI saat ini menjalankan proses quotation ("surat penawaran") secara manual, dimulai bahkan sebelum dokumen quotation itu sendiri dibuat: client bertanya lewat telepon/WA ke Marketing/Administrasi, informasi awal dicatat ala kadarnya (kalau sempat), lalu quotation disusun per proyek di Excel, dikirim/dikomunikasikan lewat WhatsApp dan email, dan disetujui secara verbal/berjenjang tanpa jejak digital. Berdasarkan BRA dan diskusi lanjutan:

- **"Bikin penawaran" adalah bottleneck tertinggi Administrasi** — tabel rincian parameter, regulasi acuan, frekuensi, qty per titik, dan harga satuan disusun manual per proyek.
- **Tahap sebelum quotation (permintaan awal client) belum tercatat sistematis** — informasi dari telepon/WA sering hanya ada di kepala/chat, rawan hilang/salah teruskan ke tim teknis (MT) untuk dinilai kelayakannya.
- **"Revisi berulang"** adalah pain point utama yang disebut Administrasi.
- **Approval quotation adalah proses approval paling kompleks** di antara seluruh dokumen SAI — melibatkan 5 tahap approval (MT, MM, Finance, Marketing, Direksi) tanpa urutan atau jejak digital yang jelas. **[v5]** Perlu ditegaskan: 5 tahap ini bukan berarti 5 orang berbeda — tahap "Marketing" dijalankan rangkap oleh siapa pun yang megang (Administrasi/MM/Direksi).
- Tidak ada satu sumber data tunggal untuk data referensi (klien, parameter uji, regulasi acuan, harga) — semua diketik ulang manual tiap kali membuat quotation baru.
- Client tidak punya cara mandiri untuk memantau tenggat pembayaran atau status pekerjaannya — semua komunikasi status masih manual lewat WA/telepon ke Administrasi.

Modul ini membangun fondasi Master Data (Klien, Parameter Uji, Regulasi Acuan, Price List), mendigitalisasi tahap **pra-quotation** (penangkapan permintaan awal + kaji ulang kelayakan teknis), dan mendigitalisasi siklus hidup Quotation dari pembuatan sampai trigger otomatis ke Work Order — dengan approval berjenjang yang terlacak, bereskalasi otomatis, dan visibilitas dasar bagi client lewat dashboard ringan.

---

## 2. Goals & Non-Goals

### Goals

1. Menyediakan satu sumber data tunggal untuk Master Data yang dipakai berulang: Klien, Parameter Uji & Regulasi Acuan, Price List referensi.
2. Mencatat permintaan awal client (Form A) secara terstruktur sejak kontak pertama (telepon/WA), lengkap dengan kaji ulang kelayakan teknis oleh MT (Form Kaji Ulang Permintaan/Tender), sebelum quotation resmi dibuat.
3. Mendigitalisasi pembuatan Quotation lengkap dengan tabel parameter (matriks, regulasi, frekuensi, qty, harga), cover/proposal, dan biaya percepatan, mengikuti format surat penawaran SAI yang sudah ada — termasuk struktur cetak 4 komponen (cover, T&C, tabel harga, Lampiran A1) yang digabung jadi satu dokumen final (Bagian 5.3, 5.6).
4. Mengurangi waktu pembuatan quotation dan jumlah siklus revisi dibanding proses manual saat ini.
5. Menyediakan approval berjenjang digital (MT → MM → Finance → Marketing → Direksi) yang terlacak, dengan status real-time dan eskalasi otomatis (SLA 1x24 jam).
6. Mendukung harga yang dapat dinegosiasikan per transaksi (bukan harga tetap per klien), dengan Price List sebagai referensi default.
7. Memicu pembuatan Work Order secara otomatis begitu Direksi memberi approval akhir.
8. Menyediakan Client Dashboard ringan (read-only) di website SAI untuk tracking status pekerjaan dan download LHU menggunakan ID pesanan, tanpa proses approval apa pun di sisi client.
9. Mendukung cetak langsung (one-click print) untuk dokumen Quotation.
10. Menjadikan dokumen ini sebagai PRD utama/fondasi sisi penjualan — perubahan/penambahan modul berikutnya dibuatkan PRD terpisah, bukan mengedit dokumen ini.

### Non-Goals (untuk rilis ini)

- **Tidak ada CRM penuh** — tidak ada leads pipeline, campaign tracking, atau manajemen funnel penjualan multi-tahap. Form A hanya mencatat *satu* titik masuk permintaan (bukan histori negosiasi/multi-touch).
- **Client Portal terbatas pada tracking + LHU saja** (lihat Bagian 5.7) — **tidak ada** approval digital oleh klien, tidak ada interaksi transaksional (bayar, revisi, negosiasi) di portal ini pada rilis ini.
- **Tidak mencakup alur quotation untuk parameter Subkontraktor** (status "Subkon" di BRA Bagian 8 Poin 5) — ditandai Out of Scope, menunggu klarifikasi F0-5.
- **Tidak ada mesin perhitungan pajak otomatis/integrasi sistem pajak eksternal** — PPN hanya berupa field terstruktur yang diisi manual.
- **Tidak mencakup modul Inventaris** (baik LIMS/bahan kimia maupun kantor/alat kalibrasi) — direkomendasikan jadi PRD terpisah (lihat Bagian 8).
- **Bukan keputusan approval final** — urutan approval di dokumen ini adalah asumsi kerja berbasis BRA, menunggu sign-off resmi Direksi di Fase 0.
- **Integrasi software "Accurate"** — belum dikonfirmasi apakah ini kebutuhan integrasi riil; ditandai Open Question, **dideprioritaskan untuk rilis ini** karena butuh klarifikasi langsung ke Product Owner yang belum bisa dijadwalkan (lihat Bagian 10).

---

## 3. Target Users

| Role | Kebutuhan Utama di Modul Ini |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Marketing** [DIKOREKSI v5] | **Bukan role/pegawai terpisah** — fungsi Marketing (Form A, approval quotation tahap Marketing) dijalankan rangkap oleh **Administrasi, Manajer Mutu (MM), atau Direksi**, siapa pun yang sedang menangani. Ketiganya perlu **All Access** untuk fungsi ini, bukan permission terbatas seperti asumsi awal BRA/TSD. Dikonfirmasi silang lewat form respons internal — tidak ada pegawai dengan jabatan "Marketing" murni |
| **Administrasi** (primary user) | Membuat, merevisi, submit quotation (termasuk dari Form A yang sudah disetujui MT); memantau status approval; input status client (approved/rejected/PO diterima) secara manual |
| **Manajer Teknis (MT)** | Melakukan kaji ulang permintaan/tender (Form Kaji Ulang) atas Form A sebelum quotation dibuat; Approve/reject quotation dari sisi kelayakan teknis (approver pertama di alur approval Quotation) |
| **Manajer Mutu (MM)** | Approve/reject dari sisi kepatuhan mutu |
| **Finance** | Approve/reject dari sisi kelayakan finansial/harga |
| **Direksi** | Approver akhir; sign-off final quotation, memicu pembuatan Work Order |
| **Client** (eksternal) | Menerima quotation via PDF/email/WA (offline); dapat memantau tenggat pembayaran & status pekerjaan serta mengunduh LHU lewat Client Dashboard (read-only, pakai ID pesanan); **[BARU v5]** mengisi & mengirim balik Lampiran A1 (Form Identitas Pelanggan) setelah PO disetujui — bukan pengguna approval di sistem ini |

---

## 4. User Stories

### Marketing

- Sebagai Marketing, saya ingin mencatat permintaan client (Form A: matriks, parameter, regulasi, qty, nama PT, alamat) langsung saat menerima telepon/WA, agar informasi tidak hilang atau salah teruskan ke tim teknis.
- Sebagai Marketing, saya ingin melihat status Form A yang saya buat (menunggu kaji ulang MT / disetujui / ditolak) agar saya bisa menindaklanjuti ke client tepat waktu.

> Catatan: sebagaimana Bagian 3, "Marketing" di sini adalah fungsi yang dijalankan rangkap oleh Administrasi/MM/Direksi, bukan role pegawai berdiri sendiri.

### Manajer Teknis (MT)

- Sebagai MT, saya ingin melakukan kaji ulang kelayakan teknis (Form Kaji Ulang Permintaan/Tender) atas Form A yang masuk, sebelum quotation resmi dibuat, agar Administrasi tidak menyusun quotation untuk permintaan yang secara teknis tidak bisa dipenuhi.

### Administrasi

- Sebagai Administrasi, saya ingin membuat Quotation baru — baik dari Form A yang sudah disetujui MT (data terisi otomatis) maupun langsung tanpa Form A (untuk client repeat) — dengan merujuk Master Data (Klien, Parameter Uji, Regulasi Acuan, Price List) agar tidak perlu mengetik ulang data referensi setiap kali.
- Sebagai Administrasi, saya ingin menambahkan banyak baris parameter uji (matriks, regulasi acuan, frekuensi, qty per titik, harga satuan) ke satu quotation agar sesuai format surat penawaran SAI yang sudah berjalan.
- Sebagai Administrasi, saya ingin mengubah harga satuan per baris dari harga referensi Price List (negosiasi) tanpa perlu approval tambahan di luar alur approval standar.
- Sebagai Administrasi, saya ingin mengisi PPN, **[BARU v5] Discount (%), Biaya Kirim**, biaya percepatan (rush fee), dan syarat pembayaran (DP/termin) sebagai field terstruktur di quotation, bukan teks bebas.
- Sebagai Administrasi, saya ingin menambahkan cover/proposal penawaran dan referensi histori LHU/pekerjaan sebelumnya untuk klien yang sama (jika ada), agar quotation terlihat lebih meyakinkan untuk client lama.
- Sebagai Administrasi, saya ingin men-submit quotation untuk approval dan melihat status real-time (sedang di approver mana) agar tidak perlu menanyakan status lewat WA.
- Sebagai Administrasi, ketika quotation di-reject, saya ingin melihat alasan reject dan merevisi quotation, dengan approval yang sudah didapat sebelumnya tetap tersimpan (tidak perlu mengulang dari awal). Saya juga ingin ada catatan konfirmasi faktur revisi agar riwayat perubahan harga/nomor jelas.
- Sebagai Administrasi, saya ingin Work Order otomatis terbuat begitu Direksi memberi approval akhir, tanpa langkah konversi manual tambahan.
- Sebagai Administrasi, saya ingin quotation otomatis kedaluwarsa 30 hari sejak terbit jika klien belum merespons, agar tidak ada quotation menggantung tanpa batas waktu.
- Sebagai Administrasi, saya ingin bisa mencetak quotation langsung dari sistem dengan satu klik — hasil cetak menggabungkan otomatis 4 komponen (cover, T&C, tabel harga, Lampiran A1 kosong) — tanpa harus export lalu buka aplikasi lain untuk print.
- **[BARU v5]** Sebagai Administrasi, saya ingin ada tempat mencatat/upload kembali Lampiran A1 yang sudah diisi client (dikirim balik setelah PO), agar data identitas client (NPWP, PIC Pendaftaran, PIC Keuangan) tersimpan di sistem — *(status: belum final, lihat Open Question Bagian 10 soal modul mana yang menangani ini)*.

### Approver (MT, MM, Finance, Marketing, Direksi)

- Sebagai approver, saya ingin menerima notifikasi saat sebuah quotation menunggu approval saya, agar tidak perlu diberi tahu manual lewat WA.
- Sebagai approver, saya ingin menerima notifikasi eskalasi jika saya belum bertindak dalam 1x24 jam, agar approval tidak diam tanpa tindak lanjut.
- Sebagai approver, saya ingin bisa approve atau reject dengan wajib mengisi alasan saat reject, agar Administrasi tahu apa yang perlu diperbaiki.

### Direksi

- Sebagai Direksi, saya ingin melihat status lengkap rantai approval sebuah quotation (siapa sudah approve, siapa masih pending) beserta ringkasan proposal (cover, biaya percepatan, harga total) sebelum memberi approval akhir/konfirmasi penawaran.

### Client

- Sebagai client, saya ingin bisa mengecek status pekerjaan pengujian saya dan mengunduh LHU menggunakan ID pesanan, tanpa perlu login akun atau menghubungi Administrasi setiap kali.
- Sebagai client, saya ingin melihat tenggat waktu pembayaran quotation saya secara jelas.
- **[BARU v5]** Sebagai client, saya menerima Lampiran A1 dalam keadaan kosong bersama quotation, dan mengisi/mengirim baliknya setelah PO disetujui sebagai syarat konfirmasi jadwal sampling.

---

## 5. Functional Requirements

### 5.1 Pra-Quotation: Form A & Kaji Ulang Permintaan/Tender

- **Form A (Custom DocType — "Client Inquiry")**: dibuat oleh Marketing saat menerima kontak awal dari client (telepon/WA). Field minimal: nama PT, alamat, PIC & kontak, matriks pengujian, parameter yang diminta, regulasi acuan (jika disebutkan client), estimasi qty, channel asal (Telepon/WA/Email/Lainnya), catatan tambahan.
- Status siklus hidup Form A: `Draft` → `Diajukan Kaji Ulang` → `Disetujui MT` / `Ditolak MT`.
- **Form Kaji Ulang Permintaan/Tender (Custom DocType, atau child/linked doc dari Form A)**: diisi oleh MT — menilai kelayakan teknis (metode tersedia, kapasitas lab, referensi regulasi yang sesuai), dengan field catatan kelayakan dan rekomendasi (Layak/Tidak Layak/Layak dengan Catatan).
- **Trigger ke Quotation**: begitu Form A berstatus `Disetujui MT`, sistem membuat **Quotation Draft** baru dengan data (klien, parameter, matriks, regulasi, qty) terisi otomatis dari Form A — Administrasi tinggal melengkapi harga, PPN, syarat pembayaran, dll.
- **Jalur alternatif tanpa Form A**: Administrasi tetap bisa membuat Quotation langsung tanpa Form A (mis. untuk client repeat/proyek internal) — Form A **tidak wajib** menjadi satu-satunya pintu masuk (lihat Open Question terkait di Bagian 10).

### 5.2 Master Data (prasyarat)

- **Customer/Klien** — perluasan DocType `Customer` ERPNext dengan field tambahan (jenis industri, PIC) sesuai rekomendasi BRA. **[BARU v5]** Field "jenis industri" kemungkinan sepadan dengan field **"Kategori Pelanggan"** (checkbox: Perusahaan/Individu-Perorangan/Institusi Pemerintah/Universitas-Sekolah/Lain-lain) yang ditemukan di header dokumen LHU — perlu dikonfirmasi apakah sama persis atau dua field berbeda (Bagian 10).
- **Test Parameter** (Custom DocType) — parameter uji, matriks pengujian (Udara Ambien/Udara Lingkungan Kerja/Emisi/Air Permukaan/Air Bersih/Air Limbah/Tanah/Sedimen), regulasi acuan (SNI/Permenkes/PP), satuan, metode uji.
- **Price List** — harga satuan referensi/default per Test Parameter, dipakai sebagai default yang bisa diubah manual saat pembuatan quotation (bukan harga mengikat per klien).

### 5.3 Quotation — Struktur Data

- Perluasan `Quotation` (Selling) ERPNext dengan **custom child table** baris parameter: Parameter Uji, Matriks, Regulasi Acuan, Frekuensi, Qty per Titik, Harga Satuan (default dari Price List, editable), Harga Total (kalkulasi otomatis).
- **Referensi Form A** (Link, opsional) — bila quotation berasal dari Form A yang disetujui.
- **Auto-numbering** mengikuti format yang sudah dipakai SAI (contoh dari BRA & 2 dokumen riil terpisah: `Quo-SAI/V/2026/075`, `Quo-SAI/V/2026/076` — bulan romawi/tahun/nomor urut). _Format persis perlu dikonfirmasi ke Administrasi saat technical design (lihat Open Questions)._
- Field terstruktur ringkasan harga, urutan mengikuti dokumen riil: **Sub Total → Discount (%) [BARU v5] → DPP → PPN (%) → Biaya Kirim [BARU v5] → Total Invoice**.
- Field terstruktur **syarat pembayaran** (DP %, termin pembayaran).
- **Biaya percepatan (rush fee)**: field jumlah hari percepatan dari target normal + persentase tambahan biaya. _(Apakah dihitung otomatis dari formula atau input manual — lihat Open Questions.)_
- **Cover/Company Profile**: bukan field dinamis per-quotation — ini adalah **dokumen company profile/proposal marketing statis** (identitas perusahaan, ruang lingkup layanan, badge akreditasi KAN, galeri kegiatan) yang sama untuk semua quotation, terdiri dari **3 halaman tetap** (cover, "Tentang Kami" + ruang lingkup pengujian, galeri kegiatan). Cukup diimplementasikan sebagai **1 file PDF standar** yang otomatis digabung/dilampirkan di depan setiap cetakan Quotation final — Administrasi **tidak perlu input ulang** setiap kali.
- **Syarat & Ketentuan (T&C)**: blok teks **template tetap/statis** (1 halaman), otomatis tercetak di setiap Quotation final, **tidak dapat diedit Administrasi per-dokumen**. Isi minimal mengikuti 12 poin standar SAI: (1) masa berlaku penawaran 30 hari kalender, (2) mekanisme quotation disetujui+stempel → otomatis jadi PO, (3) dasar perhitungan harga = jumlah sampel aktual, (4) konfirmasi jadwal sampling maks. 2 hari kerja setelah PO+Lampiran A1 diterima, (5) ketentuan keterlambatan/pembatalan sampling, (6) proses LHU (draft 10 hari kerja → review client 3 hari kerja → cetak+TTD final → soft/hardcopy, hardcopy diserahkan setelah pembayaran), (7) dokumen penagihan (Penawaran/PO/Invoice/Kwitansi/Faktur Pajak) dikirim maks. 3 hari setelah pengambilan sampel selesai, (8) syarat pembayaran (DP 50% untuk nilai ≥ Rp10.000.000, pelunasan maks. 30 hari kalender setelah invoice diterima), (9) batas revisi faktur pajak & PPh23 (maks. tanggal 10 bulan berikutnya), (10) jam penerimaan sampel (Senin–Jumat, 08.00–15.30 WIB), (11) retensi sampel sisa (maks. 1 bulan lalu dimusnahkan), (12) ketentuan pembatalan PO (H-2 normal, H-1 dengan DP = hangus). Field ini disimpan sebagai **Master Template T&C** (bukan child table per baris quotation) yang direferensikan/di-render saat cetak. **[RESOLVED v4]** Administrasi berwenang mengubah Master Template T&C ini di level institusional — namun tetap **tidak bisa** mengedit T&C per-dokumen quotation individual; setiap perubahan otomatis berlaku untuk seluruh quotation berikutnya, bukan disesuaikan per-transaksi.
- **Referensi histori LHU/pekerjaan klien**: tabel read-only opsional yang menampilkan pekerjaan/LHU sebelumnya untuk klien yang sama (jika ada), untuk memperkuat proposal — bergantung pada data dari modul LHU (PRD terpisah).
- **[STATUS DITUNDA v5] Field "Accurate"**: tiga hipotesis bersaing dan **tidak ada satu pun yang bisa dikonfirmasi dari dokumen**: (a) tagline branding "Akurat" yang muncul berulang di company profile, (b) integrasi/sinkronisasi dengan software akuntansi Accurate, (c) catatan urutan proses kerja ("pastikan data quotation akurat/final sebelum melampirkan cover dkk" — bukan field data sama sekali). Disepakati dengan Product Owner untuk **dideprioritaskan** — jangan mulai membangun apa pun berdasarkan salah satu hipotesis ini (baik field UI, apalagi integrasi API) sebelum ada klarifikasi verbal langsung dari Product Owner. Tandai `// TODO: lihat PRD Bagian 10` di kode terkait dan lanjutkan bagian lain.
- **Konfirmasi Faktur Revisi**: bukan field/log approval internal — ini adalah bagian dari klausul Syarat & Ketentuan (lihat poin 9 di atas), murni informasi batas waktu yang tercetak di dokumen, bukan mekanisme tracking di sistem.
- **[DIREFRAME v5] Lampiran A1 — Form Identitas Pelanggan**: dikonfirmasi bahwa Lampiran A1 **dikirim dalam keadaan kosong** ke client sebagai bagian ke-4 dari dokumen Quotation final, dan **diisi oleh client** (bukan Administrasi) setelah PO disetujui — pengisian ini menjadi syarat konfirmasi jadwal sampling sesuai T&C poin 4. Pertanyaan yang relevan sekarang bukan lagi "field ini masuk Master Data Customer atau lampiran per-quotation", melainkan: **bagaimana dan di modul mana** data isian balik dari client ini dicatat ke sistem — kemungkinan besar ini masuk ranah alur Work Order/Sample Tracking (karena men-trigger konfirmasi jadwal sampling), bukan modul Quotation ini. Status: **Open Question**, lihat Bagian 10.
- Field **tanggal terbit** dan **tanggal kedaluwarsa** (otomatis = tanggal terbit + 30 hari).
- Field status siklus hidup: `Draft` → `Submitted` → `MT Review` → `MM Review` → `Finance Review` → `Marketing Review` → `Direksi Review` → `Approved` / `Perlu Revisi` → (jika Approved) `Converted to Work Order`.

### 5.4 Revisi & Approval Workflow

- Approval berjenjang via Frappe Workflow Builder, urutan: **MT → MM → Finance → Marketing → Direksi** (asumsi kerja per BRA, tunduk pada sign-off Fase 0 F0-1).
  - **[DIKOREKSI v5]** Step "Marketing" **bukan dijalankan oleh role/pegawai Marketing terpisah** — dijalankan rangkap oleh Administrasi, MM, atau Direksi (siapa pun yang ditugaskan), dengan **All Access**. Ini punya implikasi teknis yang perlu diputuskan saat technical design: (a) apakah step approval "Marketing" tetap ditampilkan sebagai step terpisah di Workflow meski dilakukan orang yang sama dengan step lain (mis. MM approve dua kali — sebagai MM lalu sebagai "Marketing"), atau (b) step ini digabung/di-skip otomatis kalau approver sebelumnya sudah orang yang sama. Lihat Open Questions Bagian 10.
- Setiap step: aksi **Approve** atau **Reject**.
- **Reject**: quotation kembali ke status `Perlu Revisi` di tangan Administrasi, dengan **field alasan reject wajib diisi** oleh approver yang reject.
- **Revisi setelah reject atau setelah sebagian approval**: approval yang sudah didapat pada step-step sebelumnya **tetap valid** — workflow lanjut dari titik yang belum di-approve, tidak mengulang seluruh rantai dari awal. _(Aturan teknis persis siapa yang perlu di-notify ulang saat revisi — lihat Open Questions.)_
- **Approve final (Direksi)**: Direksi melihat halaman ringkasan berisi seluruh rantai approval + ringkasan proposal (cover, biaya percepatan, harga total) sebelum melakukan konfirmasi penawaran, yang memicu pembuatan **Work Order Pengujian** secara otomatis oleh sistem (tanpa aksi manual konversi tambahan).

### 5.5 Notifikasi & Eskalasi SLA

- Notifikasi ke approver terkait saat quotation sampai di step approval-nya (termasuk notifikasi ke MT saat Form A masuk untuk dikaji ulang).
- **Eskalasi otomatis** jika approver tidak bertindak dalam **1x24 jam** _(target eskalasi ke siapa — lihat Open Questions)_.
- Notifikasi ke Administrasi setiap ada aksi Approve/Reject, dan saat quotation kedaluwarsa.
- Notifikasi ke Marketing saat Form A yang dibuatnya disetujui/ditolak MT.

### 5.6 Interaksi dengan Client (Offline) & Cetak

- Tidak ada approval digital oleh klien di alur Quotation ini — interaksi persetujuan quotation tetap offline (PDF/email/WA).
- Sistem menyediakan **Print Format** (cetak/export PDF) quotation untuk dibagikan manual via email/WA. **[BARU v5]** Print Format final adalah gabungan 4 komponen terpisah: (1) Cover/Company Profile statis 3 halaman, (2) Syarat & Ketentuan statis 1 halaman, (3) tabel harga dinamis per-quotation, (4) Lampiran A1 kosong 1 halaman — di-merge otomatis jadi satu PDF saat generate/cetak.
- **Cetak langsung (one-click print)**: tombol cetak yang langsung membuka dialog print browser/print server tanpa perlu export-lalu-buka-aplikasi-lain terlebih dahulu.
- Administrasi meng-update status quotation secara manual berdasarkan respons client yang diterima offline (approved/rejected/PO diterima).

### 5.7 Client Dashboard (Read-Only, Tracking + LHU)

> Catatan scope: bagian ini mendefinisikan **requirement** dari sisi Quotation/Client-facing, namun implementasi datanya (status pengujian, file LHU) bergantung pada modul Work Order/Sample/LHU yang punya PRD terpisah. Bagian ini dicantumkan di sini karena merupakan janji langsung ke client yang lahir dari siklus quotation → pekerjaan → LHU.
>
> **[BLOCKER BARU v5]** Website SAI (`starlabanaltikind.com`) berjalan di WordPress, dan repo yang tersedia (`web-starlab`) ternyata hanya berisi **hasil static export/mirror** dari situs live tersebut (tanpa `wp-config.php`, database, atau plugin aktif) — bukan source yang benar-benar di-deploy. Implementasi Bagian ini **tidak bisa dimulai** sampai jelas siapa yang memegang akses WP Admin/hosting panel situs live. Lihat Bagian 7 & Open Question baru di Bagian 10.

- Halaman publik/semi-publik di website SAI (bukan bagian dari Frappe Desk internal).
- Client memasukkan **ID pesanan** (nomor Quotation atau Work Order) untuk melihat:
  - Status tracking pekerjaan (mis. Diterima → Sedang Diuji → Selesai → LHU Terbit).
  - Tombol unduh LHU (jika sudah terbit).
- **Tidak ada** aksi approval, edit, atau interaksi transaksional apa pun di halaman ini — murni read-only.
- _(Mekanisme akses — pakai ID pesanan saja tanpa autentikasi tambahan, atau perlu verifikasi tambahan (mis. email/nomor HP terdaftar) untuk mencegah orang lain menebak ID dan melihat data client lain — lihat Open Questions, ini menyangkut keamanan data.)_

### 5.8 Lokalisasi Bahasa (Non-Functional)

- Seluruh label UI yang tampil ke user (field label, judul menu, tombol, pesan notifikasi, Print Format, Client Dashboard) menggunakan **Bahasa Indonesia**.
- Nama teknis internal (nama DocType, nama field/fieldname, nama API endpoint, nama variabel di Server Script) tetap menggunakan **Bahasa Inggris**, mengikuti konvensi standar Frappe Framework.
- Aktifkan fitur **Translation** bawaan Frappe agar sistem mendukung dwibahasa (default Bahasa Indonesia, opsi beralih ke Bahasa Inggris) — teks Indonesia dikelola lewat mekanisme translation string standar Frappe, bukan hard-code di level kode, agar mudah dikelola/diperluas ke modul lain.

---

## 6. Success Metrics

_(Arah target berdasarkan pain point BRA & diskusi lanjutan — belum ada baseline terukur saat ini, sehingga dinyatakan sebagai arah perbaikan, bukan angka pasti)_

- **Waktu pembuatan quotation** (draft → submit approval pertama) menurun signifikan dibanding proses manual Excel saat ini.
- **Jumlah revisi rata-rata per quotation** menurun dibanding kondisi "revisi berulang" yang jadi pain point utama Administrasi.
- **Approval cycle time end-to-end** (submit → Direksi approve/konfirmasi) terukur dan lebih cepat dari proses verbal/WA, dibantu eskalasi SLA 1x24 jam.
- **Conversion rate Form A → Quotation** — memberi visibilitas funnel penjualan yang sebelumnya tidak tercatat sama sekali.
- **Tingkat adopsi selama masa transisi** — persentase quotation yang dibuat lewat sistem vs masih manual (relevan karena Project Plan merencanakan Quotation & Work Order berjalan paralel dengan proses manual di awal Rilis 1).
- **Insiden quotation kedaluwarsa tanpa tindak lanjut** menurun berkat expiry date otomatis + notifikasi.
- **Jumlah pertanyaan status pekerjaan yang masuk ke Administrasi via WA** menurun setelah Client Dashboard aktif (indikator tidak langsung, perlu baseline manual dulu).

---

## 7. Dependencies

- Setup environment Frappe/ERPNext & Chart of Account awal (Project Plan — bisa berjalan paralel, tidak bergantung pada resolusi Fase 0).
- **Fase 0 F0-1** (resolusi arah approval MT ↔ Administrasi, BRA Bagian 8 Poin 1) dan sign-off Direksi — urutan approval di PRD ini tetap asumsi kerja sampai ini selesai.
- **Fase 0 F0-6** (requirement gathering ke Direksi & Marketing) — sebagian sudah terisi lewat diskusi tambahan ini (alur Form A/Kaji Ulang), namun peran Marketing sebagai approver quotation tetap perlu validasi resmi.
- Modul **Work Order Pengujian** (PRD terpisah) bergantung pada trigger "Approved" dari modul ini.
- Modul **Sample Tracking & LHU** (PRD terpisah) menjadi sumber data untuk Client Dashboard (Bagian 5.7) — dashboard ini tidak bisa berfungsi penuh sebelum modul tersebut tersedia.
- **[BARU v5] Struktur repository/versioning**: modul ini diimplementasikan sebagai bagian dari custom app **`starlab_customizations`** di repo `starlab_lab_ops` (bench mono-repo berisi 4 custom app: `starlab_customizations`, `starlab_integrations`, `starlab_lab_ops`, `starlab_quality`). Source code core Frappe/ERPNext **tidak** di-vendor ke repo ini — ditarik via `bench get-app` mengikuti praktik standar. Per saat PRD ini ditulis, seluruh app masih berstatus skeleton/belum ada development.
- **[BARU v5, BLOCKER] Akses hosting/WP Admin situs live** (`starlabanaltikind.com`) — dibutuhkan sebelum implementasi Bagian 5.7 (Client Dashboard) bisa dimulai, karena repo `web-starlab` yang ada hanyalah hasil static export, bukan source yang ter-deploy. Siapa pemegang akses ini belum teridentifikasi — lihat Open Question Bagian 10.

---

## 8. Out of Scope

- CRM/lead pipeline penuh (multi-touch negotiation, campaign tracking) — Form A hanya mencatat satu titik masuk permintaan.
- Client Portal transaksional/approval — Client Dashboard pada rilis ini murni read-only (tracking + LHU).
- Alur quotation & vendor management untuk parameter Subkontraktor.
- Mesin perhitungan pajak otomatis / integrasi sistem pajak eksternal.
- Modul Inventaris — baik bahan kimia/reagen LIMS (exp date, tgl masuk) maupun inventaris kantor/alat uji (tgl kalibrasi). Direkomendasikan sebagai PRD/modul terpisah karena secara domain lebih dekat ke Stock/Asset module, bukan Quotation & Master Data. Catatan desain awal (untuk PRD terpisah nanti): reagen cocok dipetakan ke ERPNext Stock/Item + Reorder Level (sesuai TSD), sedangkan alat uji dengan jadwal kalibrasi lebih cocok ke ERPNext Asset + Asset Maintenance.
- Sign-off formal Direksi/Marketing atas urutan approval (menunggu Fase 0).
- Dukungan multi-currency (tidak disebutkan sebagai kebutuhan di BRA).
- Template/library quotation tersimpan (tidak diminta).
- Kepastian kebutuhan integrasi software "Accurate" — **[v5]** ditunda tanpa target waktu, bukan sekadar "pending konfirmasi" seperti v1-v4 (lihat Bagian 10).
- **[BARU v5]** Development/konfigurasi sisi WordPress situs live (`starlabanaltikind.com`) di luar penambahan 1 halaman/komponen Client Dashboard — pengelolaan konten website secara umum tetap di luar scope modul ini.

---

## 9. Business Process Flow (Updated)

```
Client (telepon/WA)
   │
   ▼
Marketing (fungsi rangkap Adm/MM/Direksi) ──► Form A (Client Inquiry)
   │
   ▼
Manajer Teknis ──► Kaji Ulang Permintaan/Tender (Layak / Tidak Layak)
   │ (jika Layak)
   ▼
Administrasi ──► Quotation Draft (prefilled dari Form A, atau dibuat manual tanpa Form A)
   │
   ▼
Approval Berjenjang: MT → MM → Finance → Marketing → Direksi
   │ (Approved / Konfirmasi Penawaran oleh Direksi)
   ▼
Cetak Quotation Final (Cover + T&C + Tabel Harga + Lampiran A1 kosong)
   │
   ▼
Trigger otomatis ──► Work Order Pengujian (PRD terpisah)
   │                     ▲
   │           Lampiran A1 diisi client, dikirim balik
   │           (modul penanganan: TBD, lihat Open Question)
   ▼
[Paralel, non-blocking] Client Dashboard (read-only) ──► tracking status + LHU (via ID pesanan)
```

---

## 10. Open Questions

1. **Target eskalasi SLA**: Eskalasi setelah 1x24 jam ditujukan ke siapa — atasan approver terkait, langsung ke Direksi, atau sekadar reminder ulang ke approver yang sama?
2. **Logika teknis revisi vs approval**: Saat revisi mengubah field yang jadi concern approver tertentu (misal harga berubah setelah MM approve, padahal harga itu ranah Finance) — apakah approval MM tetap valid, atau perlu aturan "approval yang levelnya setelah field yang berubah" yang di-invalidate? Perlu didalami dengan Dev1 saat technical design.
3. **Urutan approval final**: MT → MM → Finance → Marketing → Direksi masih asumsi kerja BRA — wajib divalidasi ulang setelah Fase 0 F0-1 selesai dan disetujui Direksi.
4. **Peran Marketing sebagai approver**: Dimasukkan sebagai approver wajib sesuai BRA — sekarang perannya di tahap pra-quotation (Form A) dan statusnya sebagai fungsi rangkap (bukan role terpisah) sudah lebih jelas (lihat Bagian 3), tapi implikasi teknisnya di Workflow Builder (Bagian 5.4 poin pertama) tetap perlu diputuskan saat technical design.
5. **Format auto-numbering**: Asumsi format `Quo-SAI/[bulan romawi]/[tahun]/[no urut]` berdasarkan 2 contoh dokumen riil berbeda klien (`075`, `076`) — perlu dikonfirmasi ke Administrasi apakah ini format resmi atau ada variasi lain.
6. **Perpanjangan quotation kedaluwarsa**: Jika quotation kedaluwarsa (30 hari) sebelum client merespons, apakah Administrasi butuh aksi "aktifkan ulang/extend", atau harus selalu membuat quotation baru dari nol?
7. **[DEPRIORITAS v5] Makna field "Accurate"**: Tiga hipotesis bersaing (tagline "Akurat" / integrasi software Accurate / catatan urutan proses kerja), tidak ada yang bisa dikonfirmasi dari dokumen yang tersedia. Disepakati untuk **tidak diklarifikasi dalam waktu dekat** — jangan bangun fitur/field/integrasi apa pun berdasarkan salah satu hipotesis sebelum ada klarifikasi verbal langsung dari Product Owner. Tetap ditandai `// TODO` di kode.
8. **Wajib-tidaknya Form A**: Apakah Form A menjadi satu-satunya jalur masuk sebelum Quotation dibuat, atau Administrasi tetap boleh membuat Quotation langsung (mis. untuk client repeat) tanpa melalui Form A? PRD ini berasumsi jalur langsung tetap diperbolehkan — perlu konfirmasi.
9. **Mekanisme keamanan Client Dashboard**: Apakah cukup pakai ID pesanan saja untuk mengakses tracking + LHU (risiko: ID bisa ditebak/dibagikan ke pihak lain), atau perlu verifikasi tambahan (mis. kombinasi ID + email/nomor HP terdaftar)?
10. **Perhitungan biaya percepatan (rush fee)**: Apakah dihitung otomatis via formula (mis. % tetap per hari percepatan) yang dikonfigurasi di Master Data, atau selalu input manual per quotation oleh Administrasi?
11. **Kaji Ulang Tender — siapa yang bisa override?**: Jika MT menyatakan "Tidak Layak" pada Form Kaji Ulang, apakah keputusan ini final, atau ada jalur eskalasi (mis. ke Direksi) jika Administrasi/Marketing tidak sepakat?
12. **[DIREFRAME v5] Alur input-balik Lampiran A1**: Dikonfirmasi Lampiran A1 dikirim kosong ke client dan diisi client setelah PO disetujui (bukan diisi Administrasi seperti asumsi v3/v4). Pertanyaan yang tersisa: **di modul mana** proses pencatatan data isian balik ini ditangani — apakah masih bagian dari siklus Quotation module ini (mis. sebagai attachment/field update di Quotation yang sudah Approved), atau sudah masuk ranah Work Order/Sample Tracking module (karena T&C poin 4 mengaitkannya dengan konfirmasi jadwal sampling)? Perlu klarifikasi ke Administrasi/MT.
13. **Batas komunikasi Marketing ↔ Client**: Diarahkan bahwa negosiasi awal (telepon/WA sebelum Form A) tetap privat/di luar sistem, tidak masuk Client Dashboard atau tercatat di sistem manapun. Arahan ini sudah disampaikan Product Owner, namun **status finalnya masih menunggu konfirmasi resmi Dirut** — jangan dikunci sebagai keputusan permanen sebelum sign-off tersebut.
14. ~~Kewenangan mengubah Template Syarat & Ketentuan~~ — **[RESOLVED, v4]** Administrasi berwenang mengelola/mengubah Master Template T&C di level master template (institusional), tetap **bukan** kewenangan mengedit T&C per-dokumen quotation individual.
15. **Term of Payment (TOP) default**: Dari catatan Product Owner — ada indikasi TOP default kemungkinan **7 hari**, namun ditandai dengan tanda tanya dan eksplisit butuh **konfirmasi dari Direktur (Dio Arista)**. Perlu diperjelas: TOP 7 hari ini berlaku untuk apa persisnya — batas waktu client merespons quotation, batas pembayaran DP, atau hal lain? Dan apakah ini terpisah dari ketentuan "pelunasan maks. 30 hari kalender" yang sudah tercatat di T&C poin 8?
16. **[BARU v5] Kesamaan field "jenis industri" vs "Kategori Pelanggan"**: Apakah field "jenis industri" pada perluasan Master Data Customer (Bagian 5.2) sama persis dengan field "Kategori Pelanggan" (checkbox Perusahaan/Individu-Perorangan/Institusi Pemerintah/Universitas-Sekolah/Lain-lain) yang ditemukan di dokumen LHU, atau merupakan dua field yang berbeda tujuannya?
17. **[BARU v5, BLOCKER] Kepemilikan akses hosting/WP Admin situs live**: Repo `web-starlab` yang tersedia hanya berisi hasil static export dari situs live, bukan source yang ter-deploy. Siapa di tim/perusahaan yang memegang akses WP Admin atau hosting panel `starlabanaltikind.com`? Ini blocker langsung untuk memulai implementasi Bagian 5.7 (Client Dashboard) — perlu diidentifikasi sebelum technical design dashboard dimulai.

### Ringkasan Status (v6)

**Sudah RESOLVED (tidak perlu ditanya lagi):**
- #14 — Kewenangan ubah Master Template T&C → Administrasi

**Sudah kuat bukti pendukungnya, tapi formal sign-off masih nunggu Fase 0 (tidak mendesak ditanya ulang, cukup dimonitor):**
- #3 — Urutan approval MT→MM→Finance→Marketing→Direksi (termasuk Finance) — bukti dari 2 dokumen quotation riil + gforms, tinggal nunggu sign-off resmi Direksi
- #5 — Format auto-numbering `Quo-SAI/[bulan romawi]/[tahun]/[no urut]` — bukti dari 2 dokumen riil beda klien

**Sengaja DITUNDA/dideprioritaskan (jangan ditanya dulu kecuali PO yang angkat):**
- #7 — Makna field "Accurate"

**Masih PERLU DITANYAKAN ke stakeholder terkait — ini yang harus dikejar sebelum/selama development:**

| # | Pertanyaan (versi singkat) | Tanya ke siapa |
|---|---|---|
| 1 | Eskalasi SLA 1x24 jam ditujukan ke siapa? | PO / Administrasi |
| 2 | Kalau field berubah setelah sebagian approval, approval sebelumnya invalidate atau tetap? | PO + Dev1 (technical design) |
| 4 | Step "Marketing" di Workflow Builder ditampilkan terpisah atau digabung ke approver yang sama? | PO (keputusan produk) + Dev1 (implementasi) |
| 6 | Quotation kedaluwarsa bisa di-extend atau harus buat baru? | Administrasi |
| 8 | Form A wajib jadi satu-satunya pintu masuk, atau boleh langsung buat Quotation? | Administrasi / MT |
| 9 | Client Dashboard cukup ID pesanan doang, atau perlu verifikasi tambahan? | PO (keputusan keamanan data) |
| 10 | Rush fee dihitung formula otomatis atau input manual? | Administrasi |
| 11 | Kalau MT bilang "Tidak Layak", ada jalur override/eskalasi atau final? | MT / PO |
| 12 | Data isian balik Lampiran A1 masuk sistem lewat modul Quotation atau Work Order? | PO / MT (nentuin batas modul) |
| 13 | Komunikasi Marketing↔Client di luar sistem — status final nunggu siapa? | Dirut |
| 15 | TOP default 7 hari — berlaku untuk apa persisnya, dan beda dari pelunasan 30 hari di T&C poin 8? | Direktur (Dio Arista) |
| 16 | "Jenis industri" di Master Data Customer = "Kategori Pelanggan" di LHU, atau beda? | Administrasi / MM |
| 17 | Siapa pegang akses WP Admin/hosting situs live? **(blocker Bagian 5.7)** | Tim internal / Direksi |

---

_Dokumen ini disusun berdasarkan BRA ERP SAI, TSD ERP SAI, Project Plan ERP SAI, PRD v1-v4, dan diskusi tambahan stakeholder, melalui proses bertahap untuk menyepakati asumsi kerja pada area yang belum diputuskan formal oleh SAI. Ditujukan sebagai rujukan development modul Quotation & Master Data, termasuk sebagai input teknis untuk Claude Code._
