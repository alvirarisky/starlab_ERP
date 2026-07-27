# PRD — Modul Quotation & Master Data

## ERP PT Starlab Analitik Indonesia (SAI) — Frappe/ERPNext

**Status:** Draft v8 — Revisi dari v7. Hampir seluruh Open Questions terjawab langsung oleh Product Owner (11 pertanyaan sekaligus): logika revisi, masa berlaku quotation, kewajiban Form A, formula rush fee, override Kaji Ulang, modul Lampiran A1, komunikasi informal, Term of Payment, kesamaan field kategori pelanggan, kewajaran diskon, dan makna "Accurate".

**Basis dokumen:** BRA ERP SAI, TSD ERP SAI, Project Plan ERP SAI, PRD v1-v7, Quotation PT Yanmar Indonesia (Quo-SAI/V/2026/075, versi lengkap 6 halaman) & Lampiran A1, Quotation PT Cipta Himayata (Quo-SAI/V/2026/076, dokumen rincian internal), LHU 023/LHU/SAI/III/2026, form respons pengumpulan data awal ERP (6 responden divisi), repo `starlab_ERP` & `web-starlab`, diskusi lanjutan sesi berjalan.

**Modul terkait berikutnya:** Work Order Pengujian, Sample Tracking, Hasil Uji/LHU (PRD terpisah, dependency dari modul ini)

> **Catatan untuk AI Agent:** PRD ini adalah dokumen acuan utama implementasi modul Quotation & Master Data (termasuk pra-quotation) pada proyek ERP PT Starlab Analitik Indonesia (SAI) berbasis Frappe Framework/ERPNext. Dokumen sumber tambahan (BRA, TSD, Project Plan ERP SAI) ada di folder `/docs/` pada root project ini — baca dokumen tersebut untuk konteks lebih lengkap bila diperlukan. Ikuti instruksi berikut saat men-generate atau mengubah kode berdasarkan PRD ini:
>
> 1. Nama teknis DocType, field, dan API tetap dalam Bahasa Inggris; label yang tampil ke user (label field, judul menu, pesan) dalam Bahasa Indonesia — lihat Bagian 5.8.
> 2. Jangan mengubah urutan approval (Bagian 5.4) atau logika revisi di luar yang sudah didefinisikan tanpa konfirmasi eksplisit dari Product Owner — masih berstatus asumsi kerja (lihat Bagian 10).
> 3. Setiap item di Bagian 10 (Open Questions) masih terbuka — jangan diam-diam mengambil keputusan sendiri saat implementasi; beri tanda `// TODO: lihat PRD Bagian 10` di kode terkait, atau tanyakan balik ke user.
> 4. Dokumen ini adalah PRD fondasi/utama untuk sisi penjualan (pra-quotation → quotation → trigger Work Order) — modul lanjutan (Work Order Pengujian, Sample Tracking, Hasil Uji, LHU) punya PRD terpisah yang mereferensikan modul ini; jangan menggabungkan requirement modul lain ke sini, kecuali kebutuhan tampilan (view) yang secara eksplisit dijelaskan sebagai bagian siklus quotation (lihat Bagian 5.7).
> 5. **[BARU v5]** Implementasi modul ini ditempatkan di custom app `starlab_customizations` (bukan `starlab_lab_ops`/`starlab_integrations`/`starlab_quality`) — lihat Bagian 7 untuk konteks struktur repo.

> Beberapa keputusan approval di dokumen ini adalah **asumsi kerja** mengikuti rekomendasi BRA, karena Fase 0 (resolusi konflik BRA Bagian 8 + sign-off Direksi, per Project Plan) belum selesai.

---

## Changelog v7 → v8

| # | Perubahan | Alasan |
|---|---|---|
| 1 | **[RESOLVED]** Logika revisi quotation dibalik dari keputusan v1-v7: saat quotation direvisi setelah sebagian disetujui, **seluruh approval sebelumnya direset** — wajib mengulang dari MT, bukan "lanjut dari titik terakhir" seperti asumsi sebelumnya | Konfirmasi langsung Product Owner |
| 2 | **[RESOLVED]** Masa berlaku quotation berubah dari 30 hari menjadi **45 hari**; quotation yang kedaluwarsa **dapat diaktifkan kembali**, tidak wajib dibuat baru dari nol | Konfirmasi langsung Product Owner |
| 3 | **[RESOLVED]** Form A (Client Inquiry) menjadi **satu-satunya pintu masuk wajib** sebelum Quotation dibuat — tidak ada lagi jalur langsung, termasuk untuk client repeat | Konfirmasi langsung Product Owner |
| 4 | **[RESOLVED]** Formula rush fee terkonfirmasi 2 tier: percepatan ke **5 hari kerja = +100%**, ke **7 hari kerja = +80%** dari harga dasar. Tier lain belum ada aturan baku | Konfirmasi langsung Product Owner |
| 5 | **[RESOLVED]** Keputusan "Tidak Layak" dari Manajer Teknis pada Kaji Ulang Tender bersifat **final**, tidak ada jalur eskalasi/override | Konfirmasi langsung Product Owner |
| 6 | **[RESOLVED]** Data isian balik Lampiran A1 dari client dikelola oleh **Administrasi**, tetap dalam modul Quotation | Konfirmasi langsung Product Owner |
| 7 | **[RESOLVED]** Komunikasi informal sebelum Form A tetap tidak dicatat sistematis, namun boleh dicatat di field catatan Form A bila ada tambahan relevan | Konfirmasi langsung Product Owner |
| 8 | **[RESOLVED]** Term of Payment: pelunasan invoice **maksimal 7 hari kalender** setelah invoice terbit — menggantikan asumsi "pelunasan maks. 30 hari" di draf T&C sebelumnya. Terpisah dari ketentuan DP 50% di muka | Konfirmasi langsung Product Owner |
| 9 | **[RESOLVED]** Field "jenis industri" dan "Kategori Pelanggan" dikonfirmasi sama persis — dikonsolidasikan jadi satu field (`kategori_pelanggan`) | Konfirmasi langsung Product Owner |
| 10 | **[RESOLVED]** Kewajaran diskon pada Quotation sebelum diteruskan ke Direksi menjadi tanggung jawab **Administrasi** | Konfirmasi langsung Product Owner |
| 11 | **[RESOLVED, konsep]** Field "Accurate" dikonfirmasi merujuk pada sistem akuntansi **Accurate** yang dipakai Finance — data quotation/keuangan yang sudah Approved perlu masuk ke sistem tersebut. Cakupan teknis (integrasi API otomatis vs proses manual berkala) masih perlu diklarifikasi — **jangan mulai membangun integrasi apa pun sebelum ini jelas** | Konfirmasi langsung Product Owner, klarifikasi lanjutan masih diperlukan |
| 12 | Eskalasi SLA dikonfirmasi ulang: notifikasi dikirim ke **approver yang sama**, bukan ke atasan/Direksi | Konfirmasi langsung Product Owner |

## Changelog v6 → v7

| # | Perubahan | Alasan |
|---|---|---|
| 1 | **[RESOLVED, KOREKSI]** Urutan approval Quotation final: **MT → MM → Direksi** (tiga tahap). **Finance bukan approver** — hanya read-only untuk kebutuhan pelaporan keuangan internal. **Marketing juga bukan approver** — hanya read-only untuk visibilitas pipeline penjualan. Ini mengoreksi Open Question #3/#4 di v6 (yang masih berstatus "kuat bukti, tinggal nunggu sign-off Fase 0") menjadi keputusan final yang dikonfirmasi langsung oleh Product Owner, terlepas dari status Fase 0 F0-1 yang masih berjalan untuk topik lain (arah approval MT↔Administrasi di Work Order) | Konfirmasi langsung Product Owner |
| 2 | **[KOREKSI]** Peran Marketing dikoreksi kembali dari asumsi v5 — Marketing **bukan** fungsi rangkap Administrasi/MM/Direksi seperti ditulis sebelumnya. Marketing tetap ada sebagai **role/posisi standalone** di sistem, dipertahankan sebagai antisipasi bila perusahaan merekrut posisi Marketing di kemudian hari. Untuk saat ini, siapa pun yang memegang role ini hanya memiliki akses baca pada Quotation, sama seperti Finance — tidak ada approval rangkap ke Administrasi/MM/Direksi | Konfirmasi langsung Product Owner — mengoreksi v5 changelog #1 |
| 3 | **[DITEGASKAN ULANG]** Client Dashboard (Bagian 5.7) dikonfirmasi ulang: berbasis **ID/nomor pesanan tanpa login**, sesuai desain asli dokumen ini sejak v1 — bukan versi login/Portal User yang sempat terbangun di kode pada satu iterasi pengembangan. Implementasi sedang dikoreksi kembali ke desain ini | Konfirmasi langsung Product Owner, sesuai temuan saat audit implementasi |
| 4 | **[DITURUNKAN SEVERITY]** Blocker akses WP Admin (v5 Open Q#17) — severity diturunkan. Karena Client Dashboard dihosting terpisah dari website WordPress (lihat TSD Bab 11), kebutuhan di sisi WordPress hanya menambahkan satu tautan/menu ke halaman dashboard — jauh lebih ringan dari akses hosting/tema penuh yang sebelumnya diasumsikan. Siapa pemegang akses wp-admin tetap perlu diidentifikasi, namun ini bukan lagi hard blocker untuk memulai implementasi sisi Frappe | Klarifikasi teknis lanjutan setelah v6 |
| 5 | **[BARU, di luar scope PRD ini]** Requirement Inventaris (Bagian 8) diperjelas detailnya: LIMS (reagen/bahan kimia) butuh pelacakan tanggal kedaluwarsa + tanggal masuk per batch; inventaris kantor/alat uji butuh pelacakan tanggal kalibrasi. Tetap di luar scope PRD ini, namun desain awal sudah dirintis di TSD Bagian 4.13 sebagai referensi sebelum PRD terpisah disusun | Info baru dari Product Owner |
| 6 | Field "Accurate" (Open Question #7) — tetap belum terklarifikasi, tidak ada perkembangan baru. Tetap dideprioritaskan sesuai kesepakatan v5, jangan dibangun berdasarkan tebakan | Belum ada jawaban baru dari Product Owner |

## Changelog v5 → v6

| # | Perubahan | Alasan |
|---|---|---|
| 1 | **[PENGUAT BUKTI]** Approver Finance dikonfirmasi ulang **tetap masuk** rantai approval quotation (Bagian 5.4, Open Q#3) — sempat dipertanyakan ulang berdasarkan pembacaan catatan tangan yang menyebut "Akuntan" tanpa kata "Finance" eksplisit, tapi ternyata di data gforms respondennya sendiri (Dani Ramdani) menuliskan jabatannya sebagai "Finance / Akuntan" (istilah yang dipakai bergantian secara internal, bukan 2 role berbeda). Astri (Administrasi) juga eksplisit menyebut "Finance" sebagai salah satu approver-nya. Tidak ada perubahan pada urutan approval Bagian 5.4 — ini murni penguatan bukti, bukan koreksi | Cross-check ulang antara catatan tangan PO dan data gforms atas permintaan tim |
| 2 | **[BARU]** Rekap konsolidasi status seluruh Open Questions ditambahkan sebagai referensi cepat — lihat ringkasan di akhir Bagian 10 | Memudahkan tim menindaklanjuti item yang masih perlu klarifikasi ke stakeholder terkait |

## Changelog v4 → v5

| # | Perubahan | Alasan |
|---|---|---|
| 1 | **[KOREKSI]** Peran "Marketing" sebagai role/pegawai terpisah dikoreksi di seluruh dokumen (Bagian 3, 5.4) — Marketing bukan role tersendiri, dijalankan rangkap oleh Administrasi/MM/Direksi dengan All Access | Dikonfirmasi silang dari form respons pengumpulan data awal ERP — tidak ada satu pun dari 6 responden yang menjabat "Marketing" sebagai divisi berdiri sendiri; approver list yang disebut Administrasi (Astri) juga tidak menyertakan "Marketing" sebagai entitas terpisah |
| 2 | **[BARU]** Struktur cetak Quotation final dirinci: 4 komponen terpisah yang di-*merge* — (a) Cover/Company Profile statis 3 halaman, (b) Syarat & Ketentuan statis 1 halaman, (c) tabel harga dinamis per-quotation, (d) Lampiran A1 (blank, dikirim kosong ke client) — lihat Bagian 5.3 & 5.6 | Ditemukan dari dokumen Quo 075 versi lengkap (6 halaman): urutan halaman & header masing-masing terlihat jelas sebagai 4 dokumen berbeda yang digabung, bukan 1 dokumen tunggal |
| 3 | **[KOREKSI ARAH]** Open Question Lampiran A1 (dulu #12) direframe total — bukan soal "field masuk Master Data Customer atau lampiran per-quotation", tapi soal alur input balik dari client: Lampiran A1 dikirim kosong ke client sebagai bagian quotation, diisi oleh client setelah PO disetujui, dan hasil isiannya jadi syarat konfirmasi jadwal sampling (T&C poin 4). Pertanyaan yang relevan sekarang: apakah alur input-balik ini bagian dari modul Quotation, atau sudah masuk ranah Work Order/Sample Tracking (Bagian 10) | Dikonfirmasi eksplisit oleh Product Owner setelah verifikasi isi dokumen Quo 075 asli — asumsi awal PRD v3/v4 soal Lampiran A1 diisi Administrasi ternyata keliru |
| 4 | **[BARU]** Field Discount (%) dan Biaya Kirim ditambahkan sebagai field terstruktur di ringkasan Quotation (Bagian 5.3), sejajar dengan PPN | Ditemukan di tabel ringkasan harga Quo 075: urutan Sub Total → Discount 5% → DPP → PPN 11% → B. Kirim → Total Invoice — field ini belum tercatat di PRD v1-v4 |
| 5 | **[REVISI CONFIDENCE, masih terbuka]** Field "Accurate" — muncul hipotesis ke-3: kemungkinan bukan field data sama sekali, melainkan catatan urutan proses kerja ("pastikan data quotation sudah akurat/final, baru lampirkan cover dkk"). Confidence antara 3 hipotesis (tagline "Akurat" / integrasi software Accurate / catatan urutan proses) belum bisa diputuskan dari dokumen manapun — disepakati untuk ditunda/dideprioritaskan, tidak diklarifikasi dalam waktu dekat | Disepakati dengan Product Owner: klarifikasi butuh komunikasi langsung (bukan re-interpretasi dokumen/foto), dan tidak mendesak untuk sprint saat ini |
| 6 | **[KLARIFIKASI]** Kejanggalan dugaan sebelumnya soal Quo 076 "tidak lengkap" (tanpa cover/T&C/Lampiran A1) **bukan** inkonsistensi — Quo 076 adalah dokumen rincian isi/breakdown internal, bukan dokumen final yang dikirim ke client (yang lengkap dan mengikuti format 4 komponen di atas adalah Quo 075) | Dikonfirmasi Product Owner |
| 7 | **[BARU]** Field "Kategori Pelanggan" (checkbox: Perusahaan/Individu-Perorangan/Institusi Pemerintah/Universitas-Sekolah/Lain-lain) ditemukan di dokumen LHU — kemungkinan besar ini yang dimaksud sebagai "jenis industri" pada perluasan DocType Customer di Bagian 5.2, tapi belum dikonfirmasi apakah sama persis atau field terpisah (Bagian 10) | Ditemukan di header LHU 023 |
| 8 | **[BARU]** Keputusan strategi repository: hanya custom app (`starlab_customizations`, `starlab_integrations`, `starlab_lab_ops`, `starlab_quality`) yang di-*version control* di GitHub perusahaan; source code core Frappe/ERPNext tidak di-*push* (ditarik via `bench get-app` mengikuti praktik standar ekosistem Frappe). Modul Quotation & Master Data ini ditetapkan masuk ke app `starlab_customizations` | Keputusan teknis tim, dikonfirmasi tidak ada kebutuhan khusus (air-gapped deployment, compliance internal) yang mengharuskan vendoring penuh |
| 9 | **[BARU]** Blocker baru untuk Bagian 5.7 (Client Dashboard): repo `web-starlab` yang tersedia ternyata merupakan hasil static export/mirror dari situs WordPress live (`starlabanaltikind.com`), bukan source code yang di-deploy langsung — sehingga penambahan halaman Client Dashboard butuh akses WP Admin/hosting panel situs live, yang statusnya belum jelas dimiliki siapa. Ditambahkan sebagai dependency baru di Bagian 7 dan Open Question baru di Bagian 10 | Ditemukan saat inspeksi struktur repo `web-starlab` (isinya `wp-content`/`wp-includes`/`sitemap.xml` hasil crawl statis, 1 commit, tanpa `wp-config.php`/database) |

## Changelog v1 → v2

Perubahan ini berdasarkan requirement tambahan dari diskusi stakeholder (belum tertulis di BRA/TSD asli), digabungkan ke PRD ini sesuai arahan Product Owner:

| # | Perubahan | Alasan |
|---|---|---|
| 1 | Tambah alur Pra-Quotation: Form A (permintaan awal client via telepon/WA) → Form Kaji Ulang Permintaan/Tender (review MT) → baru masuk Quotation Draft (Bagian 5.1 baru) | Mengisi gap BRA Bagian 2 & PRD v1 Non-Goal #3 ("belum ada input dari Marketing") — sekarang sudah ada alurnya |
| 2 | Tambah field pada Quotation: biaya percepatan (hari + %), cover/proposal, referensi histori LHU/PT klien, konfirmasi faktur revisi (Bagian 5.3) | Detail tambahan dari alur bisnis riil quotation SAI |
| 3 | Field "Accurate" pada Quotation ditandai belum jelas maknanya — kemungkinan integrasi software akuntansi Accurate Online, masih dikonfirmasi ke tim internal (Bagian 10, Open Question baru) | Belum ada kepastian dari Product Owner saat PRD ini disusun |
| 4 | Tambah Client Dashboard (Bagian 5.7, baru) — portal ringan di website SAI, hanya tracking status + download LHU via ID pesanan, tanpa approval | Membatalkan sebagian Non-Goal v1 "Tidak ada Client Portal" — sekarang portal read-only masuk scope, tapi portal transaksional/approval tetap Out of Scope |
| 5 | Tegaskan kebutuhan cetak langsung (one-click print), bukan sekadar export PDF (Bagian 5.6) | Permintaan eksplisit dari Administrasi |
| 6 | Konfirmasi pembagian kerja: Quotation dikerjakan Administrasi, LHU dikerjakan Manajer Mutu — tidak berubah dari v1/TSD, dicatat ulang di sini sebagai penegasan | Validasi silang, tidak ada perubahan substansi |
| 7 | Modul Inventaris (LIMS vs Kantor) — dicatat sebagai catatan silang tapi TIDAK dimasukkan ke PRD ini; direkomendasikan jadi PRD terpisah (lihat Bagian 8, Out of Scope) | Di luar cakupan domain Quotation & Master Data; lebih cocok di modul Inventory/Asset |
| 8 | Non-Goal "Tidak mencakup proses CRM/akuisisi klien sebelum quotation" direvisi — sebagian sudah in-scope (Form A sebagai pencatatan inquiry), tapi CRM penuh (leads pipeline, campaign tracking) tetap Out of Scope | Batas scope perlu tetap jelas agar tidak melebar jadi modul CRM |

## Changelog v2 → v3

Perubahan ini berdasarkan verifikasi silang terhadap dokumen quotation riil (PT Yanmar Indonesia) dan contoh LHU — beberapa interpretasi di v2 dikoreksi karena ternyata meleset dari maksud aslinya:

| # | Perubahan | Alasan |
|---|---|---|
| 1 | **[KOREKSI]** "Cover/Proposal" diperjelas: ini adalah company profile/proposal marketing statis (identitas perusahaan, ruang lingkup layanan, akreditasi, galeri kegiatan) yang sama untuk semua quotation — bukan konten dinamis yang diketik ulang per-quotation (Bagian 5.3) | Terlihat jelas dari dokumen company profile "2026 — Proposal Penawaran — All Industry One Solutions" yang formatnya generik/branding, bukan spesifik per-klien |
| 2 | **[KOREKSI]** "Konfirmasi Faktur Revisi" bukan field tracking approval internal seperti ditulis di v2 — ini adalah klausul Syarat & Ketentuan yang tercetak di body quotation (batas waktu client boleh minta revisi faktur pajak: maksimal tanggal 10 bulan berikutnya) (Bagian 5.3) | Ditemukan eksplisit di poin 9 Syarat & Ketentuan quotation PT Yanmar |
| 3 | **[BARU]** Tambah Syarat & Ketentuan (T&C) sebagai blok requirement formal — template statis/tetap, otomatis tercetak di semua quotation, tidak bisa diedit Administrasi (keputusan sudah dikonfirmasi Product Owner) (Bagian 5.3 & 5.9 baru) | Ditemukan 12 poin T&C standar (masa berlaku, mekanisme PO, jadwal sampling, proses LHU, dokumen penagihan, syarat pembayaran, faktur pajak/PPh23, retensi sampel, pembatalan) di quotation riil — belum tercatat sama sekali di v1/v2 |
| 4 | **[REVISI CONFIDENCE]** Field "Accurate" — kemungkinan besar salah dengar/typo dari tagline "Akurat" (dipakai di branding: "Akurat, Konsisten, dan Terpercaya"), bukan integrasi software Accurate Online. Confidence naik tapi belum final — tetap di Open Questions (Bagian 10) | Ditemukan tagline "Akurat" berulang di company profile |
| 5 | **[BARU]** Lampiran A1 — Form Identitas Pelanggan (identitas perusahaan + NPWP, PIC Pendaftaran, PIC Keuangan) dicatat sebagai kebutuhan baru, statusnya masih Open Question (masuk Master Data Customer atau lampiran terpisah per quotation) — lihat Bagian 10 | Ditemukan sebagai lampiran wajib di quotation PT Yanmar, belum ada padanannya di PRD v1/v2 |
| 6 | **[BARU]** Ditegaskan: komunikasi Marketing ↔ Client sebelum Form A (telepon/WA awal) tetap privat, di luar sistem — tidak masuk Client Dashboard maupun dicatat sistem. Status final pending konfirmasi Dirut (Bagian 10) | Arahan eksplisit dari Product Owner, tapi belum sign-off resmi |
| 7 | Format auto-numbering `Quo-SAI/[bulan romawi]/[tahun]/[no urut]` makin diperkuat — dua contoh riil (075 & 076, sama-sama Mei/V/2026) konsisten dengan format ini, tapi tetap disarankan konfirmasi resmi ke Administrasi sebelum dikunci (tidak diubah statusnya di Open Questions, hanya makin kuat evidence-nya) | Cross-check 2 dokumen quotation berbeda klien |

## Changelog v3 → v4

| # | Perubahan | Alasan |
|---|---|---|
| 1 | **[KOREKSI ARAH]** Field "Accurate" — dari catatan tulisan tangan asli, "accurate" tercatat sejajar/terpisah dari "Cover", sama-sama komponen pembentuk Quotation → confidence bergeser lagi ke arah kemungkinan **integrasi software Accurate**, membalikkan hipotesis v3 (tagline "Akurat"). Tetap belum final (Bagian 5.3 & 10) | Verifikasi langsung ke sumber asli (catatan tulisan tangan Product Owner) |
| 2 | **[RESOLVED]** Kewenangan mengubah Master Template Syarat & Ketentuan → **Administrasi**, karena Administrasi adalah pemilik proses quotation end-to-end. Dipindah dari Open Questions ke keputusan final (Bagian 5.3 & 10) | Konfirmasi langsung dari Product Owner |
| 3 | **[BARU]** Open Question soal Term of Payment (TOP) default — indikasi 7 hari, ditandai tanda tanya, eksplisit butuh konfirmasi Direktur (Dio) (Bagian 10) | Ditemukan di catatan tulisan tangan Product Owner |

---

## 1. Overview / Problem Statement

SAI saat ini menjalankan proses quotation ("surat penawaran") secara manual, dimulai bahkan sebelum dokumen quotation itu sendiri dibuat: client bertanya lewat telepon/WA ke Marketing/Administrasi, informasi awal dicatat ala kadarnya (kalau sempat), lalu quotation disusun per proyek di Excel, dikirim/dikomunikasikan lewat WhatsApp dan email, dan disetujui secara verbal/berjenjang tanpa jejak digital. Berdasarkan BRA dan diskusi lanjutan:

- **"Bikin penawaran" adalah bottleneck tertinggi Administrasi** — tabel rincian parameter, regulasi acuan, frekuensi, qty per titik, dan harga satuan disusun manual per proyek.
- **Tahap sebelum quotation (permintaan awal client) belum tercatat sistematis** — informasi dari telepon/WA sering hanya ada di kepala/chat, rawan hilang/salah teruskan ke tim teknis (MT) untuk dinilai kelayakannya.
- **"Revisi berulang" adalah pain point utama** yang disebut Administrasi.
- **Approval quotation adalah proses approval paling kompleks** di antara seluruh dokumen SAI — melibatkan 5 tahap approval (MT, MM, Finance, Marketing, Direksi) tanpa urutan atau jejak digital yang jelas. **[v5]** Perlu ditegaskan: 5 tahap ini bukan berarti 5 orang berbeda — tahap "Marketing" dijalankan rangkap oleh siapa pun yang megang (Administrasi/MM/Direksi).
- Tidak ada satu sumber data tunggal untuk data referensi (klien, parameter uji, regulasi acuan, harga) — semua diketik ulang manual tiap kali membuat quotation baru.
- Client tidak punya cara mandiri untuk memantau tenggat pembayaran atau status pekerjaannya — semua komunikasi status masih manual lewat WA/telepon ke Administrasi.

Modul ini membangun fondasi Master Data (Klien, Parameter Uji, Regulasi Acuan, Price List), mendigitalisasi tahap pra-quotation (penangkapan permintaan awal + kaji ulang kelayakan teknis), dan mendigitalisasi siklus hidup Quotation dari pembuatan sampai trigger otomatis ke Work Order — dengan approval berjenjang yang terlacak, bereskalasi otomatis, dan visibilitas dasar bagi client lewat dashboard ringan.

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

> Catatan: Goal #5 di atas mencantumkan rantai approval As-Is 5 tahap (masih dari draft awal dokumen ini) — rantai approval **final** yang diimplementasikan sistem sudah dikoreksi jadi 3 tahap (MT → MM → Direksi), lihat Bagian 5.4.

### Non-Goals (untuk rilis ini)

- Tidak ada CRM penuh — tidak ada leads pipeline, campaign tracking, atau manajemen funnel penjualan multi-tahap. Form A hanya mencatat satu titik masuk permintaan (bukan histori negosiasi/multi-touch).
- Client Portal terbatas pada tracking + LHU saja (lihat Bagian 5.7) — tidak ada approval digital oleh klien, tidak ada interaksi transaksional (bayar, revisi, negosiasi) di portal ini pada rilis ini.
- Tidak mencakup alur quotation untuk parameter Subkontraktor (status "Subkon" di BRA Bagian 8 Poin 5) — ditandai Out of Scope, menunggu klarifikasi F0-5.
- Tidak ada mesin perhitungan pajak otomatis/integrasi sistem pajak eksternal — PPN hanya berupa field terstruktur yang diisi manual.
- Tidak mencakup modul Inventaris (baik LIMS/bahan kimia maupun kantor/alat kalibrasi) — direkomendasikan jadi PRD terpisah (lihat Bagian 8).
- Bukan keputusan approval final — urutan approval di dokumen ini adalah asumsi kerja berbasis BRA, menunggu sign-off resmi Direksi di Fase 0.
- **[RESOLVED v8, konsep]** Integrasi software "Accurate" — dikonfirmasi merujuk pada sistem akuntansi Accurate yang dipakai Finance; data quotation/keuangan perlu masuk ke sana. Cakupan teknis (otomatis vs manual) masih di luar scope rilis ini sampai diklarifikasi lebih lanjut (lihat Bagian 10).

## 3. Target Users

| Role | Kebutuhan Utama di Modul Ini |
|---|---|
| **Marketing** [DIKOREKSI v7] | Role/posisi standalone di sistem (bukan fungsi rangkap seperti asumsi v5), dipertahankan sebagai antisipasi rekrutmen di masa depan. Mencatat Form A (permintaan awal client). Pada Quotation, hanya **read-only** untuk visibilitas pipeline penjualan — bukan approver |
| **Administrasi** (primary user) | Membuat, merevisi, submit quotation (termasuk dari Form A yang sudah disetujui MT); memantau status approval; input status client (approved/rejected/PO diterima) secara manual |
| **Manajer Teknis (MT)** | Melakukan kaji ulang permintaan/tender (Form Kaji Ulang) atas Form A sebelum quotation dibuat; Approve/reject quotation dari sisi kelayakan teknis (approver pertama di alur approval Quotation) |
| **Manajer Mutu (MM)** | Approve/reject dari sisi kepatuhan mutu (approver kedua) |
| **Finance** [DITEGASKAN v7] | **Bukan approver** — hanya read-only terhadap Quotation untuk kebutuhan pelaporan keuangan internal |
| **Direksi** | Approver akhir (ketiga); sign-off final quotation, memicu pembuatan Work Order |
| **Client** (eksternal) | Menerima quotation via PDF/email/WA (offline); dapat memantau tenggat pembayaran & status pekerjaan serta mengunduh LHU lewat Client Dashboard (read-only, pakai ID pesanan); **[BARU v5]** mengisi & mengirim balik Lampiran A1 (Form Identitas Pelanggan) setelah PO disetujui — bukan pengguna approval di sistem ini |

## 4. User Stories

### Marketing

- Sebagai Marketing, saya ingin mencatat permintaan client (Form A: matriks, parameter, regulasi, qty, nama PT, alamat) langsung saat menerima telepon/WA, agar informasi tidak hilang atau salah teruskan ke tim teknis.
- Sebagai Marketing, saya ingin melihat status Form A yang saya buat (menunggu kaji ulang MT / disetujui / ditolak) agar saya bisa menindaklanjuti ke client tepat waktu.

> Catatan: sebagaimana Bagian 3, "Marketing" di sini adalah role standalone di sistem, sesuai koreksi v7.

### Manajer Teknis (MT)

- Sebagai MT, saya ingin melakukan kaji ulang kelayakan teknis (Form Kaji Ulang Permintaan/Tender) atas Form A yang masuk, sebelum quotation resmi dibuat, agar Administrasi tidak menyusun quotation untuk permintaan yang secara teknis tidak bisa dipenuhi.

### Administrasi

- Sebagai Administrasi, saya ingin membuat Quotation baru — baik dari Form A yang sudah disetujui MT (data terisi otomatis) maupun langsung tanpa Form A (untuk client repeat) — dengan merujuk Master Data (Klien, Parameter Uji, Regulasi Acuan, Price List) agar tidak perlu mengetik ulang data referensi setiap kali. *(lihat catatan: v8 mengubah ini jadi Form A wajib, tidak ada lagi jalur tanpa Form A)*
- Sebagai Administrasi, saya ingin menambahkan banyak baris parameter uji (matriks, regulasi acuan, frekuensi, qty per titik, harga satuan) ke satu quotation agar sesuai format surat penawaran SAI yang sudah berjalan.
- Sebagai Administrasi, saya ingin mengubah harga satuan per baris dari harga referensi Price List (negosiasi) tanpa perlu approval tambahan di luar alur approval standar.
- Sebagai Administrasi, saya ingin mengisi PPN, **[BARU v5]** Discount (%), Biaya Kirim, biaya percepatan (rush fee), dan syarat pembayaran (DP/termin) sebagai field terstruktur di quotation, bukan teks bebas.
- Sebagai Administrasi, saya ingin menambahkan cover/proposal penawaran dan referensi histori LHU/pekerjaan sebelumnya untuk klien yang sama (jika ada), agar quotation terlihat lebih meyakinkan untuk client lama.
- Sebagai Administrasi, saya ingin men-submit quotation untuk approval dan melihat status real-time (sedang di approver mana) agar tidak perlu menanyakan status lewat WA.
- Sebagai Administrasi, ketika quotation di-reject, saya ingin melihat alasan reject dan merevisi quotation, dengan approval yang sudah didapat sebelumnya tetap tersimpan (tidak perlu mengulang dari awal). Saya juga ingin ada catatan konfirmasi faktur revisi agar riwayat perubahan harga/nomor jelas. *(lihat catatan: v8 membalik keputusan ini — approval sebelumnya DIRESET, wajib mengulang dari MT)*
- Sebagai Administrasi, saya ingin Work Order otomatis terbuat begitu Direksi memberi approval akhir, tanpa langkah konversi manual tambahan.
- Sebagai Administrasi, saya ingin quotation otomatis kedaluwarsa **45 hari** sejak terbit jika klien belum merespons (dan bisa diaktifkan kembali tanpa buat baru), agar tidak ada quotation menggantung tanpa batas waktu.
- Sebagai Administrasi, saya ingin bisa mencetak quotation langsung dari sistem dengan satu klik — hasil cetak menggabungkan otomatis 4 komponen (cover, T&C, tabel harga, Lampiran A1 kosong) — tanpa harus export lalu buka aplikasi lain untuk print.
- **[BARU v5]** Sebagai Administrasi, saya ingin ada tempat mencatat/upload kembali Lampiran A1 yang sudah diisi client (dikirim balik setelah PO), agar data identitas client (NPWP, PIC Pendaftaran, PIC Keuangan) tersimpan di sistem.

### Approver (MT, MM, Direksi)

- Sebagai approver, saya ingin menerima notifikasi saat sebuah quotation menunggu approval saya, agar tidak perlu diberi tahu manual lewat WA.
- Sebagai approver, saya ingin menerima notifikasi eskalasi jika saya belum bertindak dalam 1x24 jam, agar approval tidak diam tanpa tindak lanjut.
- Sebagai approver, saya ingin bisa approve atau reject dengan wajib mengisi alasan saat reject, agar Administrasi tahu apa yang perlu diperbaiki.

### Direksi

- Sebagai Direksi, saya ingin melihat status lengkap rantai approval sebuah quotation (siapa sudah approve, siapa masih pending) beserta ringkasan proposal (cover, biaya percepatan, harga total) sebelum memberi approval akhir/konfirmasi penawaran.

### Client

- Sebagai client, saya ingin bisa mengecek status pekerjaan pengujian saya dan mengunduh LHU menggunakan ID pesanan, tanpa perlu login akun atau menghubungi Administrasi setiap kali.
- Sebagai client, saya ingin melihat tenggat waktu pembayaran quotation saya secara jelas.
- **[BARU v5]** Sebagai client, saya menerima Lampiran A1 dalam keadaan kosong bersama quotation, dan mengisi/mengirim baliknya setelah PO disetujui sebagai syarat konfirmasi jadwal sampling.

## 5. Functional Requirements

### 5.1 Pra-Quotation: Form A & Kaji Ulang Permintaan/Tender

- **Form A (Custom DocType — "Client Inquiry")**: dibuat oleh Marketing saat menerima kontak awal dari client (telepon/WA). Field minimal: nama PT, alamat, PIC & kontak, matriks pengujian, parameter yang diminta, regulasi acuan (jika disebutkan client), estimasi qty, channel asal (Telepon/WA/Email/Lainnya), catatan tambahan.
- Status siklus hidup Form A: `Draft → Diajukan Kaji Ulang → Disetujui MT / Ditolak MT`.
- **Form Kaji Ulang Permintaan/Tender** (Custom DocType, atau child/linked doc dari Form A): diisi oleh MT — menilai kelayakan teknis (metode tersedia, kapasitas lab, referensi regulasi yang sesuai), dengan field catatan kelayakan dan rekomendasi (Layak/Tidak Layak/Layak dengan Catatan).
- **Trigger ke Quotation**: begitu Form A berstatus Disetujui MT, sistem membuat Quotation Draft baru dengan data (klien, parameter, matriks, regulasi, qty) terisi otomatis dari Form A — Administrasi tinggal melengkapi harga, PPN, syarat pembayaran, dll.
- **[RESOLVED v8]** Form A menjadi satu-satunya pintu masuk wajib sebelum Quotation dibuat — dikonfirmasi Product Owner bahwa seluruh quotation, termasuk untuk client repeat, harus melalui pencatatan awal Form A terlebih dahulu. Tidak ada lagi jalur pembuatan Quotation langsung.

### 5.2 Master Data (prasyarat)

- **Customer/Klien** — perluasan DocType Customer ERPNext dengan field tambahan (jenis industri, PIC) sesuai rekomendasi BRA. **[BARU v5]** Field "jenis industri" kemungkinan sepadan dengan field "Kategori Pelanggan" (checkbox: Perusahaan/Individu-Perorangan/Institusi Pemerintah/Universitas-Sekolah/Lain-lain) yang ditemukan di header dokumen LHU. **[RESOLVED v8]** Dikonfirmasi sama persis, dikonsolidasikan jadi satu field: `kategori_pelanggan`.
- **Test Parameter** (Custom DocType) — parameter uji, matriks pengujian (Udara Ambien/Udara Lingkungan Kerja/Emisi/Air Permukaan/Air Bersih/Air Limbah/Tanah/Sedimen), regulasi acuan (SNI/Permenkes/PP), satuan, metode uji.
- **Price List** — harga satuan referensi/default per Test Parameter, dipakai sebagai default yang bisa diubah manual saat pembuatan quotation (bukan harga mengikat per klien).

### 5.3 Quotation — Struktur Data

- Perluasan Quotation (Selling) ERPNext dengan **custom child table** baris parameter: Parameter Uji, Matriks, Regulasi Acuan, Frekuensi, Qty per Titik, Harga Satuan (default dari Price List, editable), Harga Total (kalkulasi otomatis).
- **[RESOLVED v8]** Referensi Form A (Link) — **wajib**, bukan opsional; setiap Quotation harus berasal dari Form A yang sudah disetujui MT.
- **Auto-numbering** mengikuti format yang sudah dipakai SAI (contoh dari BRA & 2 dokumen riil terpisah: `Quo-SAI/V/2026/075`, `Quo-SAI/V/2026/076` — bulan romawi/tahun/nomor urut). Format persis perlu dikonfirmasi ke Administrasi saat technical design (lihat Open Questions).
- Field terstruktur ringkasan harga, urutan mengikuti dokumen riil: **Sub Total → Discount (%) → DPP → PPN (%) → Biaya Kirim → Total Invoice**. **[RESOLVED v8]** Kewajaran nilai Discount menjadi tanggung jawab **Administrasi** untuk dipastikan sebelum diajukan ke rantai approval — bukan validasi otomatis sistem.
- Field terstruktur syarat pembayaran (DP %, termin pembayaran).
- **[RESOLVED v8]** Biaya percepatan (rush fee): dua tier terkonfirmasi — percepatan ke **5 hari kerja = tambahan 100%** dari harga dasar, ke **7 hari kerja = tambahan 80%**. Tier lain (jumlah hari selain 5/7) belum ada aturan baku, gunakan input manual untuk kasus tersebut sambil dicatat sebagai potensi tier baru.
- **Cover/Company Profile**: bukan field dinamis per-quotation — ini adalah dokumen company profile/proposal marketing statis (identitas perusahaan, ruang lingkup layanan, badge akreditasi KAN, galeri kegiatan) yang sama untuk semua quotation, terdiri dari 3 halaman tetap. Cukup diimplementasikan sebagai 1 file PDF standar yang otomatis digabung/dilampirkan di depan setiap cetakan Quotation final.
- **Syarat & Ketentuan (T&C)**: blok teks template tetap/statis (1 halaman), otomatis tercetak di setiap Quotation final, tidak dapat diedit Administrasi per-dokumen. Isi minimal mengikuti 12 poin standar SAI:
  1. **[RESOLVED v8]** masa berlaku penawaran **45 hari kalender** (naik dari 30 hari)
  2. mekanisme quotation disetujui+stempel → otomatis jadi PO
  3. dasar perhitungan harga = jumlah sampel aktual
  4. konfirmasi jadwal sampling maks. 2 hari kerja setelah PO+Lampiran A1 diterima
  5. ketentuan keterlambatan/pembatalan sampling
  6. proses LHU (draft 10 hari kerja → review client 3 hari kerja → cetak+TTD final → soft/hardcopy, hardcopy diserahkan setelah pembayaran)
  7. dokumen penagihan dikirim maks. 3 hari setelah pengambilan sampel selesai
  8. **[RESOLVED v8]** syarat pembayaran (DP 50% untuk nilai ≥ Rp10.000.000, pelunasan **maksimal 7 hari kalender** setelah invoice terbit — dikoreksi dari asumsi 30 hari sebelumnya)
  9. batas revisi faktur pajak & PPh23 (maks. tanggal 10 bulan berikutnya)
  10. jam penerimaan sampel (Senin–Jumat, 08.00–15.30 WIB)
  11. retensi sampel sisa (maks. 1 bulan lalu dimusnahkan)
  12. ketentuan pembatalan PO (H-2 normal, H-1 dengan DP = hangus)

  Field ini disimpan sebagai Master Template T&C yang direferensikan/di-render saat cetak. **Administrasi** berwenang mengubah Master Template T&C ini di level institusional, tidak per-dokumen.
- **Referensi histori LHU/pekerjaan klien**: tabel read-only opsional yang menampilkan pekerjaan/LHU sebelumnya untuk klien yang sama.
- **[RESOLVED v8, konsep]** Field "Accurate": dikonfirmasi merujuk pada sistem akuntansi **Accurate** yang dipakai Finance — data quotation/keuangan yang sudah Approved perlu dimasukkan ke sistem tersebut. Cakupan teknis masih terbuka: apakah dibutuhkan integrasi API otomatis (real-time sync), atau cukup proses ekspor/input manual berkala oleh Finance seperti kebiasaan saat ini — lihat Open Questions Bagian 10. **Jangan mulai membangun integrasi apa pun sebelum cakupan ini jelas**, karena effort-nya bisa sangat berbeda antara kedua opsi.
- **Konfirmasi Faktur Revisi**: bagian dari klausul Syarat & Ketentuan (lihat poin 9), murni informasi batas waktu yang tercetak di dokumen, bukan mekanisme tracking di sistem.
- **[RESOLVED v8]** Lampiran A1 — Form Identitas Pelanggan: Lampiran A1 dikirim kosong ke client sebagai bagian ke-4 dokumen Quotation final, diisi client setelah PO disetujui. Data isian balik ini dikonfirmasi dikelola oleh **Administrasi**, tetap dalam modul Quotation ini (bukan berpindah ke Work Order/Sample Tracking).
- **[RESOLVED v8]** Field tanggal terbit dan tanggal kedaluwarsa (otomatis = tanggal terbit + **45 hari**, naik dari 30 hari). Quotation yang kedaluwarsa **dapat diaktifkan kembali** oleh Administrasi (extend tanggal kedaluwarsa), tidak wajib dibuat baru dari nol.
- **[RESOLVED v8]** Field "jenis industri" pada Master Data Customer (Bagian 5.2) dan "Kategori Pelanggan" dikonfirmasi field yang sama — dikonsolidasikan menjadi satu field saja (`kategori_pelanggan`).
- Field status siklus hidup: `Draft → Submitted → MT Review → MM Review → Direksi Review → Approved / Perlu Revisi → Kedaluwarsa (dapat diaktifkan kembali) → (jika Approved) Converted to Work Order`.

### 5.4 Revisi & Approval Workflow

- Approval berjenjang via Frappe Workflow Builder, urutan final: **MT → MM → Direksi** (tiga tahap). **[RESOLVED v7]** Finance dan Marketing sama-sama **bukan approver** — keduanya hanya memiliki akses baca (read-only) terhadap Quotation, untuk kebutuhan masing-masing (pelaporan keuangan untuk Finance, visibilitas pipeline penjualan untuk Marketing). Keputusan ini dikonfirmasi langsung oleh Product Owner dan tidak lagi bergantung pada status Fase 0 F0-1 (yang membahas topik berbeda: arah approval MT↔Administrasi di modul Work Order).
- Setiap step: aksi Approve atau Reject.
- Reject: quotation kembali ke status `Perlu Revisi` di tangan Administrasi, dengan field alasan reject wajib diisi oleh approver yang reject.
- **[RESOLVED v8, DIBALIK]** Revisi setelah reject atau setelah sebagian approval: **seluruh approval sebelumnya direset** — quotation wajib mengulang rantai approval penuh dari MT lagi. Ini membalik keputusan v1-v7 yang sebelumnya berasumsi approval sebagian tetap valid. Dikonfirmasi langsung oleh Product Owner.
- Approve final (Direksi): Direksi melihat halaman ringkasan berisi seluruh rantai approval + ringkasan proposal (cover, biaya percepatan, harga total) sebelum melakukan konfirmasi penawaran, yang memicu pembuatan **Work Order Pengujian** secara otomatis oleh sistem (tanpa aksi manual konversi tambahan).

### 5.5 Notifikasi & Eskalasi SLA

- Notifikasi ke approver terkait saat quotation sampai di step approval-nya (termasuk notifikasi ke MT saat Form A masuk untuk dikaji ulang).
- **[RESOLVED v8]** Eskalasi otomatis jika approver tidak bertindak dalam **1x24 jam** — notifikasi dikirim ulang ke **approver yang sama** (bukan ke atasan atau langsung ke Direksi). Dikonfirmasi Product Owner.
- Notifikasi ke Administrasi setiap ada aksi Approve/Reject, dan saat quotation kedaluwarsa (dapat diaktifkan kembali, lihat Bagian 5.3).
- Notifikasi ke Marketing saat Form A yang dibuatnya disetujui/ditolak MT.

### 5.6 Interaksi dengan Client (Offline) & Cetak

- Tidak ada approval digital oleh klien di alur Quotation ini — interaksi persetujuan quotation tetap offline (PDF/email/WA).
- Sistem menyediakan Print Format (cetak/export PDF) quotation untuk dibagikan manual via email/WA. **[BARU v5]** Print Format final adalah gabungan 4 komponen terpisah: (1) Cover/Company Profile statis 3 halaman, (2) Syarat & Ketentuan statis 1 halaman, (3) tabel harga dinamis per-quotation, (4) Lampiran A1 kosong 1 halaman — di-merge otomatis jadi satu PDF saat generate/cetak.
- Cetak langsung (one-click print): tombol cetak yang langsung membuka dialog print browser/print server tanpa perlu export-lalu-buka-aplikasi-lain terlebih dahulu.
- Administrasi meng-update status quotation secara manual berdasarkan respons client yang diterima offline (approved/rejected/PO diterima).

### 5.7 Client Dashboard (Read-Only, Tracking + LHU)

> Catatan scope: bagian ini mendefinisikan requirement dari sisi Quotation/Client-facing, namun implementasi datanya (status pengujian, file LHU) bergantung pada modul Work Order/Sample/LHU yang punya PRD terpisah. Bagian ini dicantumkan di sini karena merupakan janji langsung ke client yang lahir dari siklus quotation → pekerjaan → LHU.

**[DITEGASKAN v7]** Website SAI (`starlabanaltikind.com`) berjalan di WordPress, dan repo yang tersedia (`web-starlab`) ternyata hanya berisi hasil static export/mirror dari situs live tersebut (tanpa `wp-config.php`, database, atau plugin aktif) — bukan source yang benar-benar di-deploy. Namun karena Client Dashboard dihosting terpisah dari WordPress (lihat TSD Bab 11) dan hanya membutuhkan satu tautan/menu dari sisi WordPress, ini bukan lagi hard blocker untuk memulai implementasi sisi Frappe — hanya menjadi prasyarat untuk langkah terakhir (menambahkan tautan di website). Lihat Bagian 7 & Open Question Bagian 10.

- Halaman publik/semi-publik di website SAI (bukan bagian dari Frappe Desk internal).
- Client memasukkan **ID pesanan** (nomor Quotation atau Work Order) untuk melihat:
  - Status tracking pekerjaan (mis. Diterima → Sedang Diuji → Selesai → LHU Terbit).
  - Tombol unduh LHU (jika sudah terbit).
- **Tidak ada** aksi approval, edit, atau interaksi transaksional apa pun di halaman ini — murni read-only.
- **[RESOLVED v7]** Mekanisme akses: dikonfirmasi cukup ID/nomor pesanan saja, tanpa autentikasi tambahan (bukan versi login/Portal User). Mitigasi risiko penebakan ID dilakukan lewat rate-limiting pada endpoint API (lihat TSD Bab 11), bukan lewat autentikasi tambahan di sisi client. Data yang dikembalikan sengaja dibatasi (status pekerjaan + tautan unduh LHU saja, tanpa data harga/finansial) untuk membatasi dampak bila ID pesanan bocor ke pihak lain.

### 5.8 Lokalisasi Bahasa (Non-Functional)

- Seluruh label UI yang tampil ke user (field label, judul menu, tombol, pesan notifikasi, Print Format, Client Dashboard) menggunakan **Bahasa Indonesia**.
- Nama teknis internal (nama DocType, nama field/fieldname, nama API endpoint, nama variabel di Server Script) tetap menggunakan **Bahasa Inggris**, mengikuti konvensi standar Frappe Framework.
- Aktifkan fitur **Translation** bawaan Frappe agar sistem mendukung dwibahasa (default Bahasa Indonesia, opsi beralih ke Bahasa Inggris) — teks Indonesia dikelola lewat mekanisme translation string standar Frappe, bukan hard-code di level kode, agar mudah dikelola/diperluas ke modul lain.

## 6. Success Metrics

*(Arah target berdasarkan pain point BRA & diskusi lanjutan — belum ada baseline terukur saat ini, sehingga dinyatakan sebagai arah perbaikan, bukan angka pasti)*

- **Waktu pembuatan quotation** (draft → submit approval pertama) menurun signifikan dibanding proses manual Excel saat ini.
- **Jumlah revisi rata-rata per quotation** menurun dibanding kondisi "revisi berulang" yang jadi pain point utama Administrasi.
- **Approval cycle time end-to-end** (submit → Direksi approve/konfirmasi) terukur dan lebih cepat dari proses verbal/WA, dibantu eskalasi SLA 1x24 jam.
- **Conversion rate Form A → Quotation** — memberi visibilitas funnel penjualan yang sebelumnya tidak tercatat sama sekali.
- **Tingkat adopsi selama masa transisi** — persentase quotation yang dibuat lewat sistem vs masih manual (relevan karena Project Plan merencanakan Quotation & Work Order berjalan paralel dengan proses manual di awal Rilis 1).
- **Insiden quotation kedaluwarsa tanpa tindak lanjut** menurun berkat expiry date otomatis + notifikasi.
- **Jumlah pertanyaan status pekerjaan yang masuk ke Administrasi via WA** menurun setelah Client Dashboard aktif (indikator tidak langsung, perlu baseline manual dulu).

## 7. Dependencies

- Setup environment Frappe/ERPNext & Chart of Account awal (Project Plan — bisa berjalan paralel, tidak bergantung pada resolusi Fase 0).
- **Fase 0 F0-1** (resolusi arah approval MT ↔ Administrasi di modul Work Order, BRA Bagian 8 Poin 1) dan sign-off Direksi — ini topik berbeda dari urutan approval Quotation (sudah resolved, lihat poin berikutnya), masih berjalan terpisah untuk modul Work Order.
- **[RESOLVED v7]** Fase 0 F0-6 (requirement gathering ke Direksi & Marketing) — peran Marketing pada Quotation sudah dikonfirmasi final oleh Product Owner (read-only, bukan approver). Kebutuhan wawancara Direksi & Marketing yang lebih luas (di luar topik ini) tetap dicatat sebagai item Project Plan yang belum tuntas.
- Modul **Work Order Pengujian** (PRD terpisah) bergantung pada trigger "Approved" dari modul ini.
- Modul **Sample Tracking & LHU** (PRD terpisah) menjadi sumber data untuk Client Dashboard (Bagian 5.7) — dashboard ini tidak bisa berfungsi penuh sebelum modul tersebut tersedia.
- **Struktur repository/versioning**: modul ini diimplementasikan sebagai bagian dari custom app **starlab_customizations** di repo `starlab_ERP` (bench mono-repo berisi 4 custom app: `starlab_customizations`, `starlab_integrations`, `starlab_lab_ops`, `starlab_quality`). Source code core Frappe/ERPNext tidak di-vendor ke repo ini — ditarik via `bench get-app` mengikuti praktik standar.
- **[DITURUNKAN SEVERITY v7]** Akses hosting/WP Admin situs live (`starlabanaltikind.com`) — dibutuhkan hanya untuk menambahkan satu tautan/menu ke Client Dashboard (bukan lagi untuk pengembangan penuh di sisi WordPress, karena dashboard dihosting terpisah). Siapa pemegang akses ini masih perlu diidentifikasi, namun bukan lagi hard blocker untuk memulai — lihat Open Question Bagian 10.

## 8. Out of Scope

- CRM/lead pipeline penuh (multi-touch negotiation, campaign tracking) — Form A hanya mencatat satu titik masuk permintaan.
- Client Portal transaksional/approval — Client Dashboard pada rilis ini murni read-only (tracking + LHU).
- Alur quotation & vendor management untuk parameter Subkontraktor.
- Mesin perhitungan pajak otomatis / integrasi sistem pajak eksternal.
- Modul Inventaris — baik bahan kimia/reagen LIMS (exp date, tgl masuk) maupun inventaris kantor/alat uji (tgl kalibrasi). Direkomendasikan sebagai PRD/modul terpisah karena secara domain lebih dekat ke Stock/Asset module, bukan Quotation & Master Data. Catatan desain awal (untuk PRD terpisah nanti): reagen cocok dipetakan ke ERPNext Stock/Item + Reorder Level (sesuai TSD), sedangkan alat uji dengan jadwal kalibrasi lebih cocok ke ERPNext Asset + Asset Maintenance.
- Sign-off formal Direksi/Marketing atas urutan approval (menunggu Fase 0).
- Dukungan multi-currency (tidak disebutkan sebagai kebutuhan di BRA).
- Template/library quotation tersimpan (tidak diminta).
- Kepastian cakupan teknis integrasi sistem akuntansi Accurate (otomatis vs manual) — **[v8]** maknanya sudah terkonfirmasi (lihat Bagian 10), namun cakupan teknisnya masih perlu klarifikasi lanjutan sebelum masuk roadmap.
- **[BARU v5]** Development/konfigurasi sisi WordPress situs live (`starlabanaltikind.com`) di luar penambahan 1 halaman/komponen Client Dashboard — pengelolaan konten website secara umum tetap di luar scope modul ini.

## 9. Business Process Flow (Updated)

```
Client (telepon/WA)
   |
   ▼
Marketing (fungsi rangkap Adm/MM/Direksi) ──► Form A (Client Inquiry)
   |
   ▼
Manajer Teknis ──► Kaji Ulang Permintaan/Tender (Layak / Tidak Layak)
   | (jika Layak)
   ▼
Administrasi ──► Quotation Draft (prefilled dari Form A, atau dibuat
manual tanpa Form A)
   |
   ▼
Approval Berjenjang: MT → MM → Direksi (Finance & Marketing: read-
only, bukan approver)
   | (Approved / Konfirmasi Penawaran oleh Direksi)
   ▼
Cetak Quotation Final (Cover + T&C + Tabel Harga + Lampiran A1 kosong)
   |
   ▼
Trigger otomatis ──► Work Order Pengujian (PRD terpisah)
   |                  ▲
   |                  Lampiran A1 diisi client, dikirim balik
   |                  (modul penanganan: TBD, lihat Open Question)
   ▼
[Paralel, non-blocking] Client Dashboard (read-only) ──► tracking
status + LHU (via ID pesanan)
```

> Catatan diagram: label "Marketing (fungsi rangkap Adm/MM/Direksi)" di baris kedua adalah sisa dari draf v5 yang sudah dikoreksi v7 — sesuai Bagian 3, Marketing sekarang adalah role standalone, bukan fungsi rangkap.

## 10. Open Questions

1. **Target eskalasi SLA** — ~~[RESOLVED v8]~~ Reminder ulang ke approver yang sama, bukan ke atasan atau Direksi.
2. **Logika teknis revisi vs approval** — ~~[RESOLVED v8, DIBALIK]~~ Seluruh approval sebelumnya direset saat ada revisi — wajib ulang dari MT. Berlaku untuk semua jenis perubahan field, tidak dibedakan per approver.
3. **Urutan approval final** — ~~[RESOLVED v7]~~ MT → MM → Direksi (tiga tahap). Finance dan Marketing read-only, bukan approver.
4. **Peran Marketing sebagai approver** — ~~[RESOLVED v7]~~ Marketing bukan approver — hanya read-only. Role tetap ada sebagai posisi standalone.
5. **Format auto-numbering**: Asumsi format `Quo-SAI/[bulan romawi]/[tahun]/[no urut]` — bukti kuat dari 2 dokumen riil, belum ada konfirmasi resmi tertulis tapi tidak mendesak.
6. **Perpanjangan quotation kedaluwarsa** — ~~[RESOLVED v8]~~ Masa berlaku 45 hari (naik dari 30), dan quotation kedaluwarsa dapat diaktifkan kembali oleh Administrasi, tidak wajib dibuat baru.
7. **Makna field "Accurate"** — ~~[RESOLVED v8, konsep]~~ Merujuk pada sistem akuntansi Accurate yang dipakai Finance. Sub-pertanyaan baru masih terbuka: apakah integrasi otomatis (API) atau tetap input manual oleh Finance — lihat item baru #19 di bawah.
8. **Wajib-tidaknya Form A** — ~~[RESOLVED v8]~~ Form A wajib menjadi satu-satunya pintu masuk, termasuk untuk client repeat. Tidak ada jalur langsung.
9. **Mekanisme keamanan Client Dashboard** — ~~[RESOLVED v7]~~ Cukup ID/nomor pesanan saja, mitigasi lewat rate-limiting di API.
10. **Perhitungan biaya percepatan (rush fee)** — ~~[RESOLVED v8]~~ Dua tier terkonfirmasi: 5 hari kerja = +100%, 7 hari kerja = +80%. Tier lain di luar itu belum ada aturan baku.
11. **Kaji Ulang Tender — siapa yang bisa override?** — ~~[RESOLVED v8]~~ Keputusan "Tidak Layak" dari MT bersifat final, tidak ada jalur eskalasi.
12. **Alur input-balik Lampiran A1** — ~~[RESOLVED v8]~~ Dikelola oleh Administrasi, tetap dalam modul Quotation ini.
13. **Batas komunikasi Marketing ↔ Client** — ~~[RESOLVED v8]~~ Tetap informal/di luar sistem; boleh dicatat di field catatan Form A bila ada informasi tambahan yang relevan.
14. **Kewenangan mengubah Template Syarat & Ketentuan** — ~~[RESOLVED, v4]~~ Administrasi, di level master template.
15. **Term of Payment (TOP) default** — ~~[RESOLVED v8]~~ TOP 7 hari berlaku untuk pelunasan invoice (maksimal 7 hari kalender setelah invoice terbit) — terpisah dan menggantikan asumsi "pelunasan maks. 30 hari" sebelumnya. DP 50% di muka tetap berlaku seperti biasa.
16. **Kesamaan field "jenis industri" vs "Kategori Pelanggan"** — ~~[RESOLVED v8]~~ Sama persis, dikonsolidasikan jadi satu field.
17. **[DITURUNKAN SEVERITY v7]** Kepemilikan akses hosting/WP Admin situs live: Karena Client Dashboard dihosting terpisah, akses ini hanya dibutuhkan untuk menambahkan satu tautan/menu — bukan lagi blocker, namun tetap perlu diidentifikasi siapa pemegangnya.
18. **[BARU v7]** Detail requirement Inventaris: Frekuensi kalibrasi standar per jenis alat, kebutuhan pencatatan vendor kalibrasi eksternal, dan cakupan pelacakan untuk Peralatan Kantor non-lab.
19. **[BARU v8]** Cakupan teknis integrasi Accurate: Apakah data quotation/keuangan perlu disinkronkan otomatis (API real-time) ke sistem Accurate, atau cukup Finance melakukan input/ekspor manual berkala seperti kebiasaan saat ini? Ini menentukan besarnya effort pengembangan — jangan mulai membangun integrasi sebelum ini jelas.

### Ringkasan Status (v8)

**Sudah RESOLVED (tidak perlu ditanya lagi):** #2, #3, #4, #6, #7 (konsep), #8, #9, #10, #11, #12, #13, #14, #15, #16 — 14 dari 19 item sudah terjawab.

**Sudah kuat bukti pendukungnya (tidak mendesak ditanya ulang):** #5 — Format auto-numbering

**Masih PERLU DITANYAKAN ke stakeholder terkait:**

| # | Pertanyaan (versi singkat) | Tanya ke siapa |
|---|---|---|
| 17 | Siapa pegang akses WP Admin/hosting situs live? (untuk tautan Client Dashboard) | Tim internal / Direksi |
| 18 | Detail requirement Inventaris (frekuensi kalibrasi, vendor eksternal, cakupan alat non-lab) | Manajer Teknis / Manajer Mutu |
| 19 | Integrasi Accurate: otomatis (API) atau tetap manual oleh Finance? | Finance / Direksi |

---

*Dokumen ini disusun berdasarkan BRA ERP SAI, TSD ERP SAI, Project Plan ERP SAI, PRD v1-v7, dan diskusi tambahan stakeholder, melalui proses bertahap untuk menyepakati asumsi kerja pada area yang belum diputuskan formal oleh SAI. Ditujukan sebagai rujukan development modul Quotation & Master Data, termasuk sebagai input teknis untuk Claude Code.*
