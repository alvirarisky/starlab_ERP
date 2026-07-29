# Ringkasan Pengerjaan Seluruh Sprint (Sprint 1 – 11)

**Cakupan:** Seluruh riwayat proyek ERP SAI dari Sprint 1 (Setup & Master Data) sampai `starlab_integrations` (TSD Sprint 9 asli). Sprint 1–4 dikerjakan sebelum sesi ini (ringkasan diambil dari `docs/audit-sebelum-sprint-5.md`); Sprint 5–11 dikerjakan dalam sesi ini, commit `6b067cd` sampai `8b988ff` di branch `develop`. Commit `53d85bb` (setelah dokumen ini pertama ditulis) menutup 4 gap yang baru ketahuan setelah cross-check ke dokumen asli SAI (`docs/dokumen asli/`) — lihat Bagian 2 & 3.18.

**Catatan penomoran:** Sprint yang kita sebut "5, 6, 7, ... 11" di percakapan adalah urutan kerja kita sendiri, BUKAN nomor Sprint resmi TSD Bagian 12. Pemetaan ke nomor TSD asli ada di tabel Bagian 1 & 2.

---

## 1. Sprint 1–4 (Sebelum Sesi Ini)

Dikerjakan oleh developer sebelumnya (dan sebagian sebagai "Fase 2" informal, di luar urutan resmi). Detail lengkap ada di `docs/audit-sebelum-sprint-5.md` — ringkasannya:

| Sprint TSD asli | Isi | Status saat audit (pra-Sprint-5) |
|---|---|---|
| **Sprint 1** — Setup & Master Data | Company, Chart of Account, Fiscal Year, Customer, Employee (7 role), Item (reagen/consumable), Test Parameter | Ada (1 commit besar, 170 file), tapi tanpa granularitas/test otomatis |
| **Sprint 2** — Quotation & Approval | Custom Field & child table Quotation, Workflow 9-state (MT→MM→Finance→Marketing→Direksi) | Fungsional inti jalan, tapi field PRD v6 belum lengkap (discount, biaya kirim, dll — baru dilengkapi Sprint 5, lihat Bagian 3.4) & auto-numbering belum sesuai format SAI (masih terbuka, lihat Bagian 5) |
| **Sprint 3** — Work Order Pengujian | DocType + WO Parameter Detail, Workflow 5-state, Role Permission | Fungsional, tapi tabel role-permission direkonstruksi manual dari narasi PDF (perlu verifikasi ulang ke TSD §7.2 asli) |
| **Sprint 4** — Sample Tracking | DocType Sample, Workflow 5-state, Dashboard Laboratorium awal (2 Number Card) | Logika Sample selesai; dashboard baru tahap awal, jauh dari 7-role penuh (baru dilengkapi Sprint 10, lihat Bagian 3.14) |
| *(informal, "Fase 2")* | Test Result + QC Detail, LHU + Print Format (kop surat placeholder), Petty Cash Entry, Document Control (ISO 17025) — semua dikerjakan lebih awal dari jadwal resminya, di luar proses sprint/code-review/test formal | Fungsional tapi tanpa Workflow (Document Control, Petty Cash) dan tanpa Custom Permission granular — baru dilengkapi Sprint 7 & 8 (lihat Bagian 3.10, 3.11) |

**Yang saat itu belum ada sama sekali** (baru dikerjakan Sprint 5 ke atas): Client Inquiry (Form A), Kaji Ulang Tender, T&C Master Template, app `starlab_integrations`, Cover/Lampiran A1 Quotation, Scheduled Job SLA/expiry, Workflow untuk Document Control/Test Result/LHU/Petty Cash/Invoice, Role Permission granular Document Master, Dashboard/Report/Notification menyeluruh.

---

## 2. Peta Sprint 5–11 (nomor kita ↔ nomor TSD asli)

| Sprint (kita) | Isi | Sprint TSD asli | Commit |
|---|---|---|---|
| 5 | Client Inquiry (Form A), Kaji Ulang Tender, TNC Master Template, ekstensi Quotation | Sprint 5 (Test Result/LHU sudah duluan dikerjakan informal sebagai "Fase 2") + bagian dari roadmap Client Inquiry yang tidak ada nomor sprint resminya di TSD | `6b067cd` |
| 6 | Scheduled task SLA/expiry Quotation, fix `docker/start.sh` | bagian dari Sprint 6 TSD | (menyatu di `6b067cd`) |
| 7 | Petty Cash Entry: Workflow + auto Journal Entry | Sprint 6 TSD (Invoice, Petty Cash & Bank Reconciliation) | `d203988` |
| — | Recheck audit Sprint 5–8 (2 bug fix, 1 cleanup, 1 false alarm) | — | `f251c2b` |
| 8 | Document Control (Document Master) Workflow + permission row-level | Sprint 7 TSD (Document Control) | `7f1732c` |
| 9 | Sales Invoice custom field/permission, tombol LHU→Invoice, akses Bank Reconciliation | Sisa Sprint 6 TSD | `cbb3e57` |
| 10 | Dashboard (7 role), Report (akses native), Notification Framework | Sprint 8 TSD (Dashboard, Report & Notification) | `b41e8c7` |
| 11 | `starlab_integrations`: WhatsApp Gateway (kerangka) + Client Portal + sinkronisasi `docker/apps.json` | Sprint 9 TSD (Integrasi WhatsApp & Client Portal) | `8b988ff` |
| — | Cross-check ke dokumen asli SAI (`docs/dokumen asli/`) → resolusi 4 gap: format nomor Quotation, konten TNC, opsi distribusi MK3/Eksternal, saldo Kas Kecil | Menjawab PRD v6 Open Question #5 + 2 gap baru yang ketahuan dari data real | `53d85bb` |

**Yang TIDAK bisa dikerjakan lewat coding** (Sprint 10 TSD asli — Migrasi Data, UAT, Go-Live): butuh data historis asli, staf yang benar-benar melakukan UAT, dan keputusan go-live bertahap. Ini PR manusia, dicatat di Bagian 6.

---

## 3. Fitur yang Sudah Selesai

### 3.1 Client Inquiry (Form A) — `starlab_customizations`
- DocType baru, naming series `FA.SAI.####.MM.YYYY`, opsional (Quotation tetap bisa dibuat manual tanpa Client Inquiry — keputusan PO).
- Workflow: Draft → Diajukan Kaji Ulang → Disetujui MT / Ditolak MT.
- Transisi Disetujui MT dipicu **dari** Kaji Ulang Tender (`sync_client_inquiry_from_kaji_ulang`), bukan tombol langsung di Client Inquiry — sesuai TSD Bagian 6.1.

### 3.2 Kaji Ulang Tender — `starlab_customizations`
- Nama disingkat dari "Kaji Ulang Permintaan/Tender" (karakter `/` tidak aman untuk nama DocType Frappe — lihat description di DocType-nya).
- Saat `rekomendasi` = Layak/Layak dengan Catatan → otomatis approve Client Inquiry + coba buat Quotation Draft.
- **Auto-create Quotation Draft** hanya isi Customer + referensi (Client Inquiry, Work Order jika ada) — TIDAK isi tabel `items` standar (lihat Bagian 5, placeholder Item). Degradasi rapi (Comment penjelasan) kalau Customer belum ada / Company default belum ada / gagal apapun — approval Kaji Ulang Tender tidak pernah gagal gara-gara ini.

### 3.3 TNC Master Template — `starlab_customizations`
- Versi T&C dengan `berlaku_sejak`; Quotation otomatis pilih versi yang berlaku SEKALI di awal (saat dibuat), lalu terkunci — Quotation lama tetap merujuk versi lama meski ada versi baru terbit.

### 3.4 Ekstensi Quotation — `starlab_customizations`
- Field baru: `discount_percent`, `biaya_kirim`, `sub_total`, `dpp`, `total_invoice` (kalkulasi otomatis: Sub Total → Discount → DPP → PPN → Biaya Kirim → Total Invoice), `client_inquiry`, `tnc_template`, `lampiran_a1`, `lampiran_a1_terisi`, `workflow_state_since`, `eskalasi_terkirim`, `kedaluwarsa_notif_terkirim`.
- `rush_fee_hari`/`rush_fee_percent` — field ADA tapi **belum diikutkan ke kalkulasi** (PRD Open Question #10 belum dikonfirmasi).
- Cetak PDF gabungan (Cover + T&C + Ringkasan Harga + Lampiran A1) lewat tombol "Cetak Quotation (Gabungan)".
- **Bug ditemukan & difix**: `tanggal_kadaluwarsa` dulu dihitung ulang tiap `validate()` tanpa syarat — sekarang di-guard `docstatus == 0` supaya tidak berubah diam-diam setelah Approved.

### 3.5 Ekstensi Customer — `starlab_customizations`
- Field baru: `jenis_industri`, `pic_name`, `kategori_pelanggan`.

### 3.6 Audit-trail fix — `starlab_lab_ops`
- `wo_hooks.py` punya beberapa `db_set()`/`frappe.db.set_value()` yang sengaja bypass Workflow engine (transisi otomatis oleh sistem, bukan user) — ini juga bypass Version log. Ditambahkan `Comment` manual di titik yang sama supaya tetap ada jejak di timeline dokumen.

### 3.7 Test Result — `starlab_lab_ops`
- Validasi: tolak (Diajukan Validasi → Ditolak) wajib isi `catatan_validasi`.
- `hasil_uji` & `qc_detail` terkunci (`read_only_depends_on: locked`) setelah Divalidasi — tidak bisa diubah lagi kecuali lewat "Batalkan Validasi".
- Workflow: Draft → Diajukan Validasi → Divalidasi/Ditolak → (Revisi kembali ke Draft).

### 3.8 LHU — `starlab_lab_ops`
- `metode_acuan` di `LHU Test Result Detail` sekarang auto-fetch dari Test Parameter (dulu kosong, TODO developer sebelumnya — sudah dikerjakan).
- Tombol "Buat Invoice" muncul begitu status LHU = Issued (lihat Bagian 3.9).

### 3.9 Sales Invoice — `starlab_customizations`
- Custom field `work_order` (Link → Work Order Pengujian), `lhu` (Link → LHU).
- Custom DocPerm sesuai TSD §7.6.
- Status "Overdue" **tidak butuh kode baru** — sudah native ERPNext (`update_invoice_status` scheduled job bawaan).
- Tombol "Buat Invoice" di LHU membuka form Sales Invoice BARU (belum tersimpan) dengan Customer/Work Order/LHU sudah terisi — item & harga tetap harus diisi manual (lihat Bagian 5, placeholder Item).

### 3.10 Petty Cash Entry — `starlab_customizations`
- Workflow: Draft → Menunggu Approval → Disetujui/Ditolak → (Revisi kembali ke Draft).
- **Disederhanakan dari TSD** (keputusan PO): approver tunggal Direksi, bukan dual approval Direksi+Finance. Finance tetap read-only.
- Saat Disetujui: auto-isi `disetujui_oleh`, auto-buat + submit Journal Entry (placeholder akun, lihat Bagian 5).
- Semua kegagalan (akun belum ada, Cost Center belum ada, error apapun) → Comment penjelasan, TIDAK pernah gagalkan approval Direksi.

### 3.11 Document Control (Document Master) — `starlab_quality`
- Status diperluas dari 3 opsi (Aktif/Dalam Revisi/Usang) jadi 6 sesuai TSD: + Draft, Menunggu Approval MM, Menunggu Approval Direksi.
- Workflow: Ajukan (oleh divisi pemilik dokumen, dinamis 7 kemungkinan) → Setujui (Manajer Mutu) → Terbitkan (Direksi) → Aktif. Dari Aktif bisa "Mulai Revisi" → Dalam Revisi → siklus ulang.
- **Model versi disederhanakan** (keputusan PO): 1 record yang berputar lewat status-nya sendiri, BUKAN 2 record terpisah per edisi. `edisi_revisi` naik dan Riwayat Revisi bertambah tiap siklus. "Usang" tetap ada di pilihan Status tapi tidak ada jalur Workflow otomatis ke sana.
- Permission row-level: baca dibatasi ke dokumen yang didistribusikan/dimiliki divisinya (Manajer Mutu & Direksi lihat semua); tulis dibatasi ke dokumen milik divisi sendiri (Manajer Teknis lebih sempit lagi: cuma dokumen level IKM).
- Saat Terbitkan: otomatis catat Riwayat Revisi + notifikasi ke semua divisi di Distribusi.

### 3.12 Bank Reconciliation — akses role Finance
- Bank Account, Bank Transaction, Bank Reconciliation Tool, Bank Statement Import — semua native ERPNext, defaultnya cuma role "Accounts Manager/User". Role custom "Finance" sekarang dikasih akses lewat Custom DocPerm.

### 3.13 Report — akses native
- Accounting Receivable (Aging Piutang) & Bank Reconciliation Statement (Rekonsiliasi Bank) — 2 report yang TSD minta ternyata **sudah native ERPNext**, cuma role Finance belum bisa akses. Dikasih lewat mekanisme "Custom Role" (bukan edit report langsung — report standard tidak bisa di-save langsung di luar `developer_mode`).
- Rekap Kepatuhan Dokumen Mutu & Laporan Keuangan Operasional — filter & role diperbaiki.

### 3.14 Dashboard — 7 role
- 21 Number Card + 5 chart tren, dibundel jadi 7 `Dashboard` (Direksi, Marketing, Administrasi, Finance, Laboratorium, Manajer Teknis, Manajer Mutu).
- Beberapa metrik di TSD **sengaja di-skip** karena tidak bisa dinyatakan sebagai count/sum sederhana tanpa jadi menyesatkan: saldo kas GL asli, conversion rate Quotation→WO, histori order per klien. Ini butuh Query Report custom kalau mau dikerjakan, bukan Number Card.

### 3.15 Notification Framework
- Diimplementasi sebagai Python custom (hook `on_update` + scheduled job harian), BUKAN Notification DocType deklaratif seperti disarankan TSD — supaya bisa dites langsung di `bench console`, konsisten dengan cara kerja sepanjang sesi ini.
- Approval Pending (Quotation, Work Order, Test Result, Petty Cash Entry, Document Master) — notifikasi SEGERA saat masuk state approval, terpisah dari eskalasi SLA Quotation yang sudah ada (yang baru jalan setelah macet >1×24 jam).
- Test Result Ditolak → notifikasi ke analis pembuatnya.
- Sample Deadline Mendekat (H-2) / Terlewat, Sample Retensi Jatuh Tempo — scheduled job harian.
- Invoice Due (H-3) / Overdue — scheduled job harian.
- Stock Minimum — **tidak butuh kode baru**, sudah native ERPNext (`reorder_item` scheduled job bawaan).
- **Bug ditemukan & difix**: `frappe.sendmail` langsung raise error (bukan gagal diam-diam) kalau belum ada Email Account default — situasi yang sangat mungkin terjadi di site baru. Semua pemanggilan sendmail (lama & baru) sekarang dibungkus supaya gagal kirim notifikasi tidak pernah gagalkan transaksi/scheduled job yang memicunya.

### 3.16 `starlab_integrations` (app baru)
- **WhatsApp Settings** (Single DocType) + `whatsapp.py`: kerangka siap pakai untuk 3 provider (Fonnte, Twilio, WhatsApp Business API) + opsi Custom. Default nonaktif (`enabled=0`) — belum ada akun asli.
- Dipanggil sebagai kanal TAMBAHAN opsional dari notifikasi yang sudah ada (Bagian 3.15) — tidak mengganggu kanal Email/Notification Log yang sudah jalan kalau `starlab_integrations` belum di-install atau WhatsApp Settings belum diisi.
- **Client Portal** (`/status-klien`): halaman untuk klien login lihat status LHU + ringkasan Invoice-nya sendiri. Pakai mekanisme "Portal User" bawaan ERPNext (sama seperti `/orders`, `/invoices` native) — bukan logika baru.

### 3.17 Perbaikan infrastruktur Docker
- `docker/apps.json` ternyata menunjuk ke branch/repo yang macet di Sprint 1–4, terpisah dari `develop`. Disinkronkan (`app-starlab-customizations`, `app-starlab-quality`, `app-starlab-lab-ops` di-update ke state `develop` saat ini; `app-starlab-integrations` dibuat baru) supaya `docker/start.sh` benar-benar mendeploy kode terbaru.

### 3.18 Resolusi 4 gap dari dokumen asli SAI — `starlab_customizations` / `starlab_quality` (commit `53d85bb`)
Ground truth diambil langsung dari dokumen bisnis asli SAI di `docs/dokumen asli/` (Quotation, Daftar Induk Dokumen dan Distribusi, Laporan Keuangan Operasional Harian) — bukan dari BRA/PRD/TSD lagi, karena 4 hal ini memang tidak/belum lengkap dijelaskan di sana.

- **Quotation auto-numbering** (`quotation_hooks.py`, hook `autoname`): format `Quo-SAI/[bulan romawi]/[tahun]/[no urut 3 digit]`, dikonfirmasi dari 2 Quotation asli berbeda (`Quo-SAI/V/2026/075` & `.../076`, sama-sama bulan Mei — nomor urut naik per TAHUN, bukan reset tiap bulan). Menggantikan `naming_series` default ERPNext lewat `doc_events["Quotation"]["autoname"]` di `hooks.py` — dipilih karena `autoname` doc-event dijalankan Frappe SEBELUM `naming_series` bawaan DocType, jadi tidak perlu ubah skema Quotation.
- **TNC Master Template v01**: diisi via patch (`patches/seed_tnc_master_template.py`, terdaftar di `patches.txt` `[post_model_sync]`) dengan 12 poin Syarat & Ketentuan asli, diambil verbatim dari dokumen "Quo 075-PT Yanmar Indonesia". Sebelumnya field `konten_tnc` kosong/placeholder.
- **Document Distribution — opsi "MK3" dan "Eksternal"**: ditambahkan ke `divisi` (Select) karena ternyata ada di data distribusi real SAI tapi belum ada di sistem. Keduanya tidak punya Role/user sistem yang cocok (tidak ada role K3 di 7-role model TSD; Eksternal memang di luar organisasi) — jadi acknowledgment untuk 2 opsi ini tetap manual/di luar sistem, tidak lewat notifikasi otomatis seperti divisi lain (`ROLE_BY_DIVISION_CODE.get()` yang sudah ada otomatis mengembalikan `None` untuk keduanya, tidak perlu perubahan kode lain).
- **Laporan Keuangan Operasional — kolom "Saldo Kas Kecil"**: ditambahkan mengikuti format ledger asli ("Laporan Keuangan SAI - Operasional Harian") yang punya kolom SALDO berjalan. Dihitung dari `GL Entry` akun `Kas Kecil - {abbr}` yang benar-benar terpaut ke tiap Journal Entry yang tampil di laporan — BUKAN dari nominal Petty Cash Entry langsung, karena Petty Cash Entry cuma catatan pengajuan/approval, bukan mutasi buku besar itu sendiri. Baris kategori "Petty Cash" sengaja tampil `Saldo = kosong`.

Semua 4 perubahan sudah di-migrate & functional test lewat `bench execute`/`bench console` di sandbox sebelum di-push. Panduan testing manual (lewat Desk UI) ada di Bagian 7.10.

### 3.19 Finance read-only di Quotation, 7 Workspace per role, histori LHU klien — `starlab_customizations`
- **Quotation: Finance bukan approver lagi**. State "Menunggu Approval Finance" dihapus total dari Workflow Quotation (`fixtures/workflow.json`) — alur approval sekarang MT → MM → Marketing → Direksi langsung (Manajer Mutu approve langsung lanjut ke Marketing). `PENDING_APPROVAL_STATES`/`ROLE_BY_STATE` di `tasks.py` disesuaikan. Custom DocPerm Finance di Quotation diset `read=1, write=0, submit=0` — benar-benar read-only, cuma untuk keperluan lihat data buat laporan keuangan.
  - **Petty Cash Entry dual approval (Finance+Direksi) SENGAJA TIDAK dikerjakan** meski awalnya diminta — ini membalikkan keputusan PO #5 (dual approval sudah pernah eksplisit disederhanakan jadi Direksi-saja). Dikonfirmasi ulang ke PO saat dikerjakan: tetap Direksi-saja, tidak jadi dibalik.
  - Test otomatis pertama di seluruh proyek yang beneran jalan & lolos: `starlab_customizations/starlab_customizations/tests/test_quotation_workflow_permission.py` — membuktikan user dengan role Finance TIDAK punya workflow transition apa pun di Quotation, di state manapun (MT/MM/Marketing/Direksi), plus assert permission read-only. Lihat catatan penting soal test discovery di Bagian 6.
- **7 Workspace per role** (Direksi, Marketing, Administrasi, Finance, Laboratorium, Manajer Teknis, Manajer Mutu) — `starlab_customizations/starlab_customizations/workspace/<slug>/<slug>.json`, masing-masing berisi Number Card + Chart (reuse dari Dashboard yang sudah ada di Bagian 3.14) + Shortcut ke DocType terkait, dan dibatasi visibility-nya lewat child table `roles` (cuma muncul di Desk untuk user dengan role itu).
  - **Penting — Workspace TIDAK disinkronkan lewat mekanisme `fixtures` di `hooks.py`** seperti Dashboard/Number Card/dsb. Sempat dicoba lewat `fixtures/workspace.json` dan langsung ke-delete otomatis oleh `bench migrate` di langkah "Removing orphan Workspaces", karena Frappe mensinkronkan Workspace sebagai *module doc* (satu file JSON per folder di `starlab_customizations/workspace/<nama>/<nama>.json`, sama seperti DocType/Report), bukan lewat fixtures. Kalau mau nambah/ubah Workspace lagi ke depan, ikuti pola folder ini, JANGAN didaftarkan di `fixtures`.
- **Field `histori_lhu_klien`** di Quotation (Table, read-only, child DocType baru "Quotation LHU History"): daftar LHU milik Customer yang sama dengan Quotation ini. Di-fetch ulang tiap form dibuka lewat `doc_events["Quotation"]["onload"]` (`quotation_hooks.py::_populate_histori_lhu_klien`) — SENGAJA tidak disimpan permanen di baris Quotation, supaya selalu mencerminkan LHU terbaru milik client tersebut secara live, termasuk LHU yang baru terbit setelah Quotation dibuat.

### 3.20 Kanban Board, kop surat resmi, icon Workspace, default filter shortcut
- **Kanban Board "Sample per Status" & "Work Order Pengujian per Status"** — dibuat via patch (`starlab_lab_ops/patches/seed_kanban_boards.py`) yang manggil `quick_kanban_board()` bawaan Frappe (logika sama persis dengan tombol "Create Kanban Board" di List View), jadi kolomnya otomatis mengikuti opsi Select field `status` masing-masing DocType, bukan di-hardcode.
- **Kop surat resmi PT Starlab Analitik Indonesia** — dibuat sebagai 1 record `Letter Head` terpusat (`starlab_customizations/letter_head/pt_starlab_analitik_indonesia/`, `is_default=1`), bukan hardcode HTML terpisah di tiap Print Format. Isi (nama, alamat, telepon, email, no. akreditasi KAN LP-2063-IDN) diambil verbatim dari kop surat asli di `docs/dokumen asli/LHU 023- PT Starlab Analitik Indoensia.pdf`. Print Format **Quotation Ringkasan Harga** (sebelumnya sama sekali tanpa kop surat) dan **LHU Resmi** (sebelumnya placeholder "[LOGO PLACEHOLDER]"/"Jl. Contoh Alamat Placeholder") sekarang sama-sama render `{{ letter_head }}` di baris paling atas.
  - **Gap yang masih tersisa**: file gambar logo & badge akreditasi KAN yang asli (raster/vector) belum ada sebagai aset terpisah — cuma kelihatan di render PDF dokumen asli. Representasinya sementara teks "KAN / LP-2063-IDN" di kop surat. Ganti ke `<img>` di `content` Letter Head begitu SAI kirim file logo aslinya.
  - **Penting — Letter Head, sama seperti Print Format & Workspace, disinkronkan sebagai *module doc*** (`starlab_customizations/letter_head/<slug>/<slug>.json`), BUKAN lewat `fixtures`.
- **Icon per Workspace** — 7 Workspace sudah punya icon Lucide yang berbeda-beda sejak awal dibuat (Direksi=briefcase, Marketing=megaphone, Administrasi=clipboard-list, Finance=circle-dollar-sign, Laboratorium=flask-conical, Manajer Teknis=settings, Manajer Mutu=shield-check) — dicek ulang, semua sudah tersimpan benar & berbeda-beda di database dev, dan semua nama icon valid (dicocokkan ke daftar asli di `frappe/public/icons/lucide/icons.svg`). Kalau di instance lain masih kelihatan "briefcase" semua, kemungkinan besar instance itu belum `bench migrate` dengan fixture terbaru, bukan bug di kode.
- **Default filter per shortcut Workspace** — pakai field `stats_filter` (Code/JSON) di Workspace Shortcut, yang di Frappe dobel fungsi: badge angka di kartu shortcut DAN `frappe.route_options` yang otomatis kepasang saat shortcut diklik (`shortcut_widget.js`). Contoh: shortcut Quotation di Workspace Direksi → `{"workflow_state": "Menunggu Approval Direksi"}`; Manajer Teknis → `{"workflow_state": "Menunggu Approval MT"}`; dst — masing-masing difilter ke state/status yang jadi *actionable queue* role tersebut, konsisten dengan Number Card yang sudah ada.
  - **Bug ditemukan & difix**: shortcut "Document Distribution" di Workspace Manajer Mutu (dibuat di Bagian 3.19) ternyata tidak akan pernah bisa dibuka — itu child table (`istable: 1`), tidak punya List View sendiri. Dihapus dari daftar shortcut; datanya tetap kelihatan lewat Number Card "Distribusi Belum Dibaca" (yang memang query lewat `parent_document_type`, jadi valid) dan lewat form Document Master langsung.

### 3.21 Client Dashboard tanpa login + Marketing bukan approver Quotation — `starlab_integrations` / `starlab_customizations`
- **Client Dashboard nomor pesanan tanpa login** (PRD v8 Bagian 5.7 / TSD Bab 11) — endpoint baru `starlab_integrations.tracking.track_order` (`@frappe.whitelist(allow_guest=True)` + `@rate_limit(limit=30, seconds=60)`), menerima nomor Quotation ATAU Work Order Pengujian, mengembalikan status pekerjaan + status/tautan unduh LHU kalau sudah terbit — **tidak pernah** mengembalikan data harga/finansial apa pun. Halaman publik di `/tracking` (`www/tracking.html` + `.py`) — form sederhana + JS `frappe.call`, murni client-side fetch ke endpoint di atas, tidak ada pengecekan login sama sekali.
  - **Diverifikasi beneran lewat HTTP guest** (bukan cuma manggil fungsi Python langsung): jalanin `bench serve` sementara, `curl` ke endpoint TANPA cookie session — responsnya `Set-Cookie: sid=Guest` (native Frappe, konfirmasi request ini benar-benar dianggap tamu anonim) dan tetap dapat data yang benar. Halaman `/tracking` juga dicek langsung return HTTP 200 tanpa redirect ke `/login`.
  - `/status-klien` (versi login/Portal User, dari Sprint 10 lama) tetap ada apa adanya sebagai kanal alternatif — sesuai TSD Bab 11, bukan kanal utama.
- **Marketing bukan approver Quotation** — pola persis sama seperti Finance (Bagian 3.19): state "Menunggu Approval Marketing" dihapus total dari Workflow Quotation (MM approve langsung ke Direksi), `PENDING_APPROVAL_STATES`/`ROLE_BY_STATE` di `tasks.py` disesuaikan, Custom DocPerm Marketing di Quotation diset `write=0` (read tetap 1). **Role "Marketing", Employee dengan Designation Marketing, dan Workspace "Marketing" TIDAK dihapus** — cuma kemampuan approve di workflow Quotation yang hilang, persis seperti perlakuan Finance.
  - Shortcut Quotation di Workspace Marketing (dibuat Bagian 3.20) yang sebelumnya filter ke `workflow_state: "Menunggu Approval Marketing"` ikut diperbaiki jadi tanpa filter (nampilin semua Quotation) — Marketing sekarang murni visibilitas pipeline, tidak punya "actionable queue" approval lagi.
  - Test `test_quotation_workflow_permission.py` direfactor: logika Finance & Marketing digabung lewat mixin (`_QuotationNonApproverPermissionMixin`, BUKAN subclass `TestCase` supaya tidak ikut ke-discover sebagai test class sendiri), dipakai oleh 2 test class konkret (`...FinancePermission`, `...MarketingPermission`) — total 4 test, semua lolos.

### 3.22 PRD v8 Sprint 12 — Penyesuaian Quotation Berdasarkan Keputusan Product Owner — `starlab_customizations`
8 keputusan PO baru yang mengubah/mempertegas beberapa perilaku Quotation & dokumen terkait dari sprint-sprint sebelumnya:

1. **Reset penuh approval saat konten diubah pasca-approval sebagian** — sebelumnya, approver di tahap MM/Direksi (yang punya `allow_edit` di state mereka sendiri) bisa mengedit konten Quotation tanpa lewat Tolak/Revisi, sehingga approval MT/MM yang sudah ada seolah tetap berlaku untuk konten yang sudah berubah. `quotation_hooks.py::_revert_to_mt_if_content_changed_mid_approval` sekarang membandingkan field numerik/teks penting + isi tabel `parameter_detail` sebelum/sesudah save (`get_doc_before_save()`); kalau ada perubahan konten SAAT state masih di "Menunggu Approval MM" atau "Menunggu Approval Direksi" (bukan hasil transisi Workflow yang sah), state di-`db_set` paksa balik ke "Menunggu Approval MT" + notifikasi ulang ke Manajer Teknis. Perubahan di tahap MT sendiri (sebelum approval pertama) tidak memicu reset apa pun — itu memang wajar.
2. **Masa berlaku Quotation 30 → 45 hari + state "Kedaluwarsa" + reaktivasi** — `EXPIRY_DAYS` di `quotation_hooks.py` naik jadi 45. Workflow Quotation (`fixtures/workflow.json`) dapat state baru "Kedaluwarsa" (`doc_status=1`, `allow_edit: Administrasi`) plus action "Aktifkan Kembali" (transisi balik ke "Approved"). Scheduled job harian `tasks.py::check_quotation_expiry` sekarang benar-benar memindahkan Quotation Approved yang lewat `tanggal_kadaluwarsa` ke state "Kedaluwarsa" (sebelumnya cuma kirim notifikasi tanpa mengubah state). "Aktifkan Kembali" adalah transisi Workflow asli (aksi Administrasi genuine) yang memperpanjang `tanggal_kadaluwarsa` 45 hari dari hari ini — tidak perlu bikin Quotation baru dari nol.
3. **`client_inquiry` wajib di Quotation** — Custom Field `Quotation.client_inquiry` sekarang `reqd=1`. Membalikkan keputusan PRD v6 (Bagian 4 baris 3) yang tadinya menjadikan Form A opsional — sekarang seluruh Quotation, termasuk client repeat, wajib melalui pencatatan Client Inquiry terlebih dahulu. `_create_quotation_draft` di `client_inquiry_hooks.py` sudah otomatis mengisi field ini sejak awal, jadi tidak ada perubahan logika di jalur auto-create.
4. **Field baru `tingkat_percepatan`** (Select) di Quotation — opsi: Normal (default), "7 Hari Kerja (+80%)", "5 Hari Kerja (+100%)", "Lainnya (Input Manual)". `quotation_hooks.py::_apply_tingkat_percepatan` auto-isi `rush_fee_hari`/`rush_fee_percent` untuk 2 tier yang sudah dikonfirmasi PO; pilih "Normal" mengosongkan kedua field rush fee; pilih "Lainnya" membiarkan `rush_fee_hari`/`rush_fee_percent` diisi manual (field lama dari sebelumnya, sekarang jadi fallback untuk kasus di luar 2 tier baku).
5. **Konsolidasi `jenis_industri` + `kategori_pelanggan` di Customer** — dikonfirmasi PO kedua field ini identik/redundan. Patch baru `consolidate_customer_kategori_pelanggan.py` (`[post_model_sync]`) memindahkan nilai `jenis_industri` ke `kategori_pelanggan` untuk Customer yang belum terisi `kategori_pelanggan` (skip + `frappe.log_error` kalau ada konflik nilai atau nilai di luar opsi baku, untuk direview manual), lalu menghapus Custom Field `Customer-jenis_industri`. Field `pic_name` yang sebelumnya `insert_after: jenis_industri` dipindah ke `insert_after: customer_type`.
6. **Konten T&C Master Template diperbarui** — bukan mengedit versi `01` yang sudah lama dipakai Quotation lama, tapi menambah **versi baru `02`** (patch `seed_tnc_master_template_v2.py`, `berlaku_sejak` = tanggal patch dijalankan) dengan poin masa berlaku "45 hari" (bukan 30) dan poin pelunasan "7 (tujuh) hari kalender setelah invoice diterima" (bukan 30 hari). Quotation lama tetap merujuk v01 apa adanya; Quotation baru otomatis memilih v02 lewat logika pemilihan versi terbaru yang sudah ada di `_set_active_tnc_template`.
7. **Payment Terms Sales Invoice: due date = tanggal invoice + 7 hari** — hook baru `invoice_hooks.py::set_due_date` (doc_event `Sales Invoice.validate`) meng-set `due_date = posting_date + 7 hari` untuk invoice draft. Terdaftar di `hooks.py::doc_events`.
8. **Test untuk seluruh 7 poin di atas** — lihat Bagian 7.14 untuk daftar file test & cara jalankan; ringkas: 24 test baru/direfactor di `starlab_customizations`, semua lolos (`bench run-tests --app starlab_customizations`).

> **Catatan implementasi**: item 1 & 2 (arah Approved→Kedaluwarsa) memakai pola `doc.db_set(...)` bypass yang sudah dipakai di `wo_hooks.py` sejak sprint-sprint awal — dipilih karena keduanya dipicu sistem (scheduled job / deteksi otomatis saat save), bukan aksi eksplisit user yang punya role terkait. "Aktifkan Kembali" (Kedaluwarsa→Approved) sebaliknya memakai transisi Workflow asli karena itu memang aksi user (Administrasi) yang genuine. Perhatikan juga: Frappe memicu `on_update_after_submit` (bukan `on_update`) untuk save pada dokumen yang docstatus-nya sudah 1→1 (kasus "Aktifkan Kembali") — `on_update` Quotation didaftarkan di kedua event di `hooks.py` supaya logika reaktivasi tetap jalan.

### 3.23 Rush fee masuk kalkulasi Total Invoice, bersih-bersih TODO basi, tutup gap test coverage — `starlab_customizations` / `starlab_lab_ops` / `starlab_quality` / `starlab_integrations`

**a. Rush fee masuk kalkulasi Total Invoice (dampak uang)**
- Field baru `rush_fee_amount` (Currency, read-only) di Quotation = `sub_total x rush_fee_percent / 100`, dihitung di `quotation_hooks._calculate_price_summary`. Urutan ringkasan harga sekarang: Sub Total → **Rush Fee** → Discount (%) → DPP → PPN (%) → Biaya Kirim → Total Invoice.
- **⚠️ ASUMSI KERJA, BELUM DIKONFIRMASI KE PO**: `rush_fee_amount` ditambahkan ke Sub Total SEBELUM Discount dihitung, jadi Discount % ikut memotong nominal Rush Fee juga (bukan cuma Sub Total murni). Ini interpretasi kerja dari instruksi "tambahkan baris baru setelah sub_total, sebelum discount" — **perlu divalidasi eksplisit ke PO sebelum dipakai untuk Quotation produksi beneran**. Kalau PO memutuskan Rush Fee seharusnya tidak ikut didiskon, tinggal ganti base discount di `_calculate_price_summary` dari `base_after_rush_fee` balik ke `doc.sub_total` saja (satu baris, lokasinya sudah ditandai di komentar kode).
- Print Format "Quotation Ringkasan Harga" (`starlab_customizations/print_format/quotation_ringkasan_harga/`) menampilkan baris Rush Fee di antara Sub Total dan Discount, tapi HANYA kalau `rush_fee_amount > 0` (disembunyikan untuk Quotation Normal/tanpa percepatan) — plus catatan kecil di footer print yang mengingatkan status ASUMSI di atas.
- 3 test baru (`IntegrationTestQuotationRushFeeInTotal` di `test_quotation_fields.py`) mengunci formula ini secara eksplisit — kalau urutan kalkulasinya berubah nanti (menuruti keputusan PO), test-test ini akan gagal dan menandai tempat yang perlu disesuaikan.

**b. TODO basi di `check_quotation_sla` dibersihkan**
- Komentar di `tasks.py::check_quotation_sla` sebelumnya masih bilang "target eskalasi belum dikonfirmasi PO (PRD v6 Open Question #1)" — padahal PRD v8 sudah menjawabnya (reminder ulang ke approver yang sama, bukan ke atasan/Direksi langsung). Komentar diperbarui untuk menyatakan ini KEPUTUSAN FINAL PO, bukan default sementara. Tidak ada perubahan logika, murni akurasi dokumentasi kode.

**c. Gap test coverage 0-test ditutup sebagian**
- **`starlab_lab_ops`**: `test_sanity.py` (2 test) dipindah dari lokasi salah (`starlab_lab_ops/tests/`, di luar `frappe.get_app_path`) ke lokasi yang benar-benar ke-discover `bench run-tests` (`starlab_lab_ops/starlab_lab_ops/starlab_lab_ops/tests/`, sejajar dengan folder `doctype/`) — bug yang sama persis dengan yang sempat ditemukan & dicatat di Bagian 6 untuk app ini sebelumnya, sekarang benar-benar difix.
- **`starlab_quality`**: stub kosong `IntegrationTestDocumentMaster` (0 test method) sekarang berisi 4 test nyata: siklus Draft→Menunggu Approval MM→Menunggu Approval Direksi→Aktif, tolak di tahap MM (dengan & tanpa `catatan_revisi` — harus divalidasi wajib), dan satu test yang **mengunci temuan penting**: opsi Status "Usang" memang ada di field (`document_master.json`), tapi TIDAK ADA jalur Workflow otomatis mana pun yang menujunya — sesuai keputusan PO eksplisit yang sudah didokumentasikan di description field DocType-nya sendiri (1 record berputar lewat status, bukan 2 record lama/baru — lihat Bagian 4 baris 7). **Lihat catatan penting di bawah** soal ini.
- **`starlab_integrations`**: `test_tracking.py` (4 test, baru) untuk `track_order()` — guest bisa akses tanpa login (divalidasi lewat `frappe.is_whitelisted()`, jalur pemeriksaan yang sama persis dipakai `frappe.handler` untuk request HTTP asli), response tidak pernah membocorkan field harga/finansial (pengecekan rekursif ke seluruh struktur response terhadap daftar kata kunci harga), dan rate-limiting (`@rate_limit(limit=30, seconds=60)`) benar-benar memblokir permintaan ke-31 dalam window yang sama (disimulasikan dengan mengisi `frappe.local.request` — di luar konteks HTTP asli, decorator ini no-op).
- **Masih 0 test**: `kaji_ulang_tender`, `tnc_master_template`, `client_inquiry`, `petty_cash_entry` (stub `starlab_customizations`) — di luar scope task ini, lihat Bagian 6.

> ⚠️ **Perlu keputusan PO/user**: instruksi task ini juga meminta test yang membuktikan "dokumen Document Master lama otomatis jadi Usang saat versi baru Aktif" — tapi behavior itu **tidak ada di kode saat ini** dan justru bertentangan dengan keputusan PO yang sudah didokumentasikan eksplisit (Bagian 4 baris 7 & description `document_master.json`): modelnya sengaja 1 record yang berputar lewat status-nya sendiri per edisi (bukan 2 record lama/baru), dan "Usang" sengaja TIDAK dapat transisi otomatis. Daripada membangun ulang logika production baru yang membalik keputusan itu tanpa konfirmasi, test yang ditulis (`test_status_option_usang_exists_but_has_no_automatic_transition`) justru MENGUNCI perilaku "tidak ada auto-transition" sebagai baseline yang terverifikasi. Kalau PO memang mau mengubah keputusan lama itu, butuh instruksi eksplisit dulu sebelum diimplementasikan.

> **Catatan lingkungan (bukan perubahan kode)**: menulis test nyata untuk Document Master pertama kali di sesi ini memicu bug lama di seeding default Department milik ERPNext core (`Company.on_update` gagal dengan `Could not find Parent Department: All Departments`) — dipicu lewat rantai dependency `Document Master` → child table `Document Revision` → Link `diubah_oleh` (Employee) → Company, saat Frappe mencoba auto-generate test record Employee. Dihindari dengan `IGNORE_TEST_RECORD_DEPENDENCIES = ["Employee"]` di `test_document_master.py` (tidak ada test di bawah yang butuh Employee ter-generate otomatis). Bug seeding Department itu sendiri murni masalah environment/ERPNext core, di luar scope perbaikan sesi ini.

### 3.24 Polish tampilan Client Dashboard + branding dasar — `starlab_customizations` / `starlab_integrations`

Logo resmi PT Starlab Analitik Indonesia (`docs/dokumen asli/SAI Logo_name.png`, dari user) sekarang jadi aset kode, bukan cuma dipakai di kop surat sebagai teks:

- **Aset logo** — logo asli (2000x2000, banyak whitespace) di-crop jadi 2 varian dan dibundel sebagai static asset app (`public/images/`, bukan File doctype — ini aset branding yang menempel ke kode, bukan data upload user):
  - `sai-logo.png` (256px, ikon bintang+LAB saja tanpa nama perusahaan) — dipakai untuk App Logo Desk & header halaman `/tracking`. Dibundel di KEDUA app (`starlab_customizations` untuk Desk, `starlab_integrations` untuk halaman publik) supaya `/tracking` tidak bergantung diam-diam ke asset app lain yang tidak ada di `required_apps`-nya.
  - `sai-favicon.png` (64px, ikon yang sama) — dipakai sebagai favicon.
  - Warna brand yang diambil presisi dari file asli (bukan tebakan): navy `#050066`, cyan `#11A8E0`, merah `#FE0000`.
- **Patch baru `set_sai_branding.py`** (`[post_model_sync]`) — idempotent, mengeset:
  1. `Website Settings.app_logo` & `.favicon` ke path asset di atas.
  2. `Color` doc baru (`#11A8E0`) + `Website Theme` custom baru ("PT Starlab Analitik Indonesia") dengan `primary_color` mengarah ke situ, di-set sebagai `Website Settings.website_theme` aktif.
  3. **Temuan penting**: field `Website Theme.primary_color` (mekanisme resmi Frappe) ternyata **tidak lagi mengontrol warna tombol** di versi Frappe ini — sistem desain "espresso" bawaan Frappe men-style `.btn-primary` dari token `--btn-primary` yang di-hardcode ke abu-abu gelap (`--surface-gray-10`), sama sekali tidak membaca `$primary`/`primary_color` (dikonfirmasi dengan membaca source SCSS-nya langsung, bukan tebakan). Kalau cuma set `primary_color` seperti yang diminta secara harfiah, tombol tetap abu-abu gelap, bukan biru default Bootstrap seperti dugaan awal tapi juga bukan warna brand. **Fix**: tambahan `custom_scss` override eksplisit (`--btn-primary` + `.btn-primary` dengan `!important`) di field `Website Theme.custom_scss` — field escape-hatch resmi yang memang disediakan untuk kasus seperti ini, dirender setelah semua import sehingga menang di cascade. Sudah diverifikasi sampai ke compiled CSS yang benar-benar disajikan browser (`.btn-primary{background-color:#11a8e0 !important}`), bukan cuma dicek field-nya kesimpen di DB.
- **`tracking.html` dirombak**:
  - Logo + heading + subjudul di atas form (bukan cuma teks polos).
  - "Mencari..." diganti spinner CSS murni (tanpa library eksternal).
  - Hasil pencarian sekarang per-Work-Order jadi card terpisah (border kiri aksen cyan, background lembut), status pakai badge warna (hijau = selesai/disetujui/issued, kuning = proses/draft/menunggu, merah = dibatalkan/ditolak/superseded, biru = revised/diterima) — klasifikasi berdasarkan kata kunci di teks status supaya otomatis menangani ketiga vocabulary status yang beda-beda (WO, LHU, Quotation) tanpa mapping tetap yang gampang basi.
  - Form input+tombol pakai flexbox dengan `@media (max-width: 480px)` supaya tombol jadi full-width & stack ke bawah di layar HP, bukan kepotong side-by-side.
  - Semua interpolasi teks tetap lewat `frappe.utils.escape_html` (tidak ada perubahan postur keamanan dari versi sebelumnya).

### 3.25 2 Workspace domain baru: CRM & LIMS — `starlab_customizations`

Selain 7 Workspace per-role yang sudah ada (Bagian 2-3.20-3.21), sekarang ada 2 Workspace **domain-based** yang menyatukan pandangan lintas-role untuk 1 alur kerja utuh — **tidak menghapus/mengganti 7 Workspace lama**, murni tambahan:

- **CRM** (icon `trending-up`, warna `yellow`, `sequence_id: 8`) — pintasan: Client Inquiry, Kaji Ulang Tender, Quotation, Customer, TNC Master Template. Number Card: 4 baru per status Client Inquiry (Draft/Diajukan Kaji Ulang/Disetujui MT/Ditolak MT — belum pernah ada Number Card untuk DocType ini sebelumnya) + 3 lama yang di-reuse (Quotation Draft/Approved/Rejected, sama seperti yang dipakai Workspace Marketing, tidak diduplikasi).
- **LIMS** (icon `clipboard-check`, warna `light-blue`, `sequence_id: 9`) — pintasan: Work Order Pengujian, Sample, Test Result, Test Parameter, LHU, plus 2 pintasan Kanban Board yang sudah ada ("Sample per Status", "Work Order Pengujian per Status" dari Bagian 3.20) ditautkan lewat mekanisme native Frappe (`Workspace Shortcut.doc_view = "Kanban"` + `kanban_board`, BUKAN link URL manual). Number Card: 4-4-nya reuse dari `starlab_lab_ops` (Sample Belum Diuji, Sample Sedang Diuji, Test Result Menunggu Validasi, LHU Draft Menunggu Diterbitkan — sama persis dengan yang dipakai Workspace Laboratorium/Manajer Teknis), tidak ada Number Card baru dibuat untuk LIMS.
- **`roles` dikosongkan di keduanya** (sesuai permintaan) — semua user internal yang login bisa melihat Workspace ini; pembatasan AKSI (bisa create/edit/approve atau tidak) tetap sepenuhnya dari Role Permission per-DocType seperti biasa, visibility Workspace bukan mekanisme pembatasan.
- **Chart funnel "Form A → Quotation → Approved" (baru, custom)** — dicek dulu ke Workspace Direksi & Marketing, TIDAK ada chart funnel/konversi lintas-DocType yang sudah ada di sana (keduanya cuma punya "Tren Quotation Dibuat", chart tren waktu biasa, beda konsep) — jadi ini genuinely baru, bukan reuse. **Temuan penting**: Frappe versi ini tidak punya tipe chart "Funnel" bawaan (opsi field `type` di Dashboard Chart cuma Line/Bar/Percentage/Pie/Donut/Heatmap, dicek langsung dari `dashboard_chart.json`) — apalagi funnel yang diminta melintasi 2 DocType berbeda (Client Inquiry + Quotation) sama sekali tidak bisa direpresentasikan lewat chart_type bawaan manapun (Count/Sum/Average/Group By semuanya terikat ke SATU document_type). Diimplementasikan sebagai **Dashboard Chart Source custom** (`starlab_customizations/dashboard_chart_source/funnel_form_a_ke_approved/`, pola persis sama dengan yang dipakai ERPNext sendiri untuk chart lintas-DocType, lihat `erpnext/stock/dashboard_chart_source/warehouse_wise_stock_value/`) yang menghitung 3 angka (total Client Inquiry, total Quotation, Quotation Approved) dan ditampilkan sebagai Bar chart menurun — secara visual berfungsi sebagai funnel meski secara teknis bukan tipe "Funnel" asli.
- **Dashboard Chart Source BUKAN fixture** — disinkronkan sebagai "module doc" (folder `dashboard_chart_source/<nama>/` berisi `.py` + `.json` + `.js`, persis pola Report/Print Format/Workspace), bukan lewat `fixtures/dashboard_chart.json`. Dashboard Chart-nya sendiri (yang mereferensikan source ini) TETAP fixture seperti chart-chart lain di app ini.

> ⚠️ **Bug pra-existing ditemukan & difix saat testing manual Bagian ini** (bukan cuma soal CRM/LIMS -- ini nyangkut SEMUA 7 Workspace role lama juga): login Desk sebagai role custom manapun (Direksi, Marketing, Laboratorium, dst) selalu gagal total merender halaman apapun ("Not permitted... User X does not have doctype access via role permission for document Page"), padahal login sebagai Administrator normal. Akar masalahnya: SPA Desk selalu mencoba resolusi route lewat DocType `Page` (mekanisme fallback lawas, dipanggil di setiap load halaman) sebelum settle ke Workspace yang benar; DocType `Page` bawaan Frappe defaultnya cuma bisa dibaca role `Administrator`/`System Manager` (dicek langsung dari `page.json`), jadi role custom manapun kena 403 alih-alih 404 "tidak ketemu" yang sebenarnya cuma informational/harmless. Ini kemungkinan besar SUDAH ada dari awal project -- baru ketauan sekarang karena baru kali ini ada yang benar-benar login Desk pakai akun role selain Administrator (semua testing sebelumnya lewat `bench console`/test otomatis yang tidak melalui jalur ini). **Fix**: `Custom DocPerm` baru, `read`-only ke role `All` (built-in, otomatis dipegang semua user) untuk DocType `Page` -- bukan doctype data bisnis, aman dibuka lebar. Setelah fix, resolusi gagal balik jadi 404 senyap (sama seperti behavior Administrator), Desk render normal buat semua role.

---

## 4. Keputusan yang Sudah Ditentukan (PO Decisions)

| # | Topik | Keputusan | Alasan/Konteks |
|---|---|---|---|
| 1 | Status "Fase 2" (Test Result, LHU, Petty Cash, Document Control) | Dianggap selesai/delivered, bukan prioritas ulang — polish hanya kalau memang sedang disentuh | Sudah fungsional dari sebelum Sprint 5, tinggal dipoles |
| 2 | Auto-numbering Quotation | **[Superseded oleh commit `53d85bb`]** Awalnya: tetap default ERPNext, jangan hardcode. Sekarang: `Quo-SAI/[bulan romawi]/[tahun]/[no urut]`, dikonfirmasi dari 2 dokumen Quotation asli SAI | PRD v6 Open Question #5 terjawab lewat `docs/dokumen asli/` — lihat Bagian 3.18 |
| 3 | Client Inquiry (Form A) | **[Superseded oleh PRD v8 Sprint 12]** Awalnya: opsional, bukan satu-satunya jalan bikin Quotation. Sekarang: **wajib** (`client_inquiry` jadi `reqd=1`), tidak ada lagi jalur bikin Quotation tanpa Form A | Keputusan PO baru — lihat Bagian 3.22 poin 3 |
| 4 | Lampiran A1 | Field attach/update sederhana di Quotation, bukan DocType/Workflow terpisah | Simplifikasi scope |
| 5 | Dual approval Petty Cash Entry | Disederhanakan: Direksi saja (bukan Direksi+Finance) | Keputusan eksplisit setelah ditanya — **dikonfirmasi ulang & tetap dipertahankan** saat diminta lagi belakangan (lihat Bagian 3.19) |
| 6 | Akun GL Journal Entry Petty Cash | Placeholder + TODO jelas, bukan skip fitur | Belum ada Chart of Accounts riil dari Finance |
| 7 | Model versi Document Master | 1 record berputar lewat status-nya sendiri, bukan 2 record terpisah per edisi | Menghindari perubahan skema (`document_no` unique) di DocType existing |
| 8 | WhatsApp Gateway | Bikin kerangka siap pakai, TIDAK isi kredensial asli | Belum ada akun/API key provider WhatsApp |
| 9 | Jangan refactor besar-besaran Quotation/Work Order/Sample tanpa konfirmasi | Dipegang sepanjang sesi — semua perubahan ke 3 DocType itu murni tambahan (field baru, guard baru), tidak ada restrukturisasi skema lama | Belum ada test otomatis yang bisa mendeteksi regresi |

---

## 5. Placeholder / TODO — Perlu Diisi Sebelum Produksi

| Item | Lokasi | Yang perlu dilakukan |
|---|---|---|
| Akun GL Journal Entry Petty Cash | `starlab_customizations/petty_cash_hooks.py` — `"Kas Kecil - {abbr}"` / `"Beban Operasional Kantor - {abbr}"` | Finance konfirmasi nama akun COA asli, sesuaikan kode kalau beda |
| Cost Center default Company | Company Setup | Pastikan Company punya Cost Center default terisi (biasanya otomatis dari Setup Wizard) |
| Rush fee Quotation | **[Sebagian terjawab]** Sekarang sudah masuk kalkulasi Total Invoice (`rush_fee_amount`, lihat Bagian 3.23a) — tapi posisi di urutan kalkulasi (ditambahkan sebelum Discount, jadi ikut terdiskon) masih ASUMSI kerja | PRD v6 Open Question #10 — bagian "apakah rush fee masuk kalkulasi" sudah terjawab (ya), bagian "di mana posisinya relatif ke Discount" masih perlu konfirmasi eksplisit ke PO |
| Target eskalasi SLA Quotation | `starlab_customizations/tasks.py::check_quotation_sla` | PRD v6 Open Question #1 — sekarang default "reminder ulang ke approver yang sama", ganti kalau ternyata harus ke atasan |
| WhatsApp Settings | Desk → cari "WhatsApp Settings" | Isi provider, API URL, API Key, Nomor Pengirim begitu sudah pilih & daftar provider (Fonnte/Twilio/WhatsApp Business API), lalu centang "Aktifkan" |
| Item master untuk Quotation/Invoice | `Quotation Parameter Detail`, tombol "Buat Invoice" di LHU | Test Parameter belum ditautkan ke Item master ERPNext — auto-create Quotation/Invoice sengaja TIDAK isi tabel `items` standar karena ini. Kalau mau full-otomatis, perlu diputuskan dulu: bikin 1 Item generik "Jasa Pengujian" atau mapping per parameter |
| LHU: status custom vs native submit | `starlab_lab_ops` — LHU sudah punya Custom DocPerm submit/cancel/amend yang nganggur (DocType belum `is_submittable`) | Diputuskan dulu: pindah ke native submit (buang status custom Draft/Issued/Revised/Superseded) atau hapus DocPerm yang nganggur |

---

## 6. Catatan / PR untuk Kita (Follow-up)

- **Sprint 10 TSD asli (Migrasi Data, UAT, Go-Live)** — tidak bisa dikerjakan lewat sesi coding. Butuh: file data historis (Excel/Google Drive lama), staf yang benar-benar melakukan UAT per role, keputusan go-live bertahap (Quotation/WO dulu → Sample/QC → sisanya).
- **Hampir tidak ada test otomatis yang beneran jalan** — audit awal berkali-kali nge-flag ini sebagai risiko nomor satu. **[Update Bagian 3.23c]** Ditutup sebagian: `starlab_lab_ops` (2 test), `starlab_quality` (4 test, Document Master), `starlab_integrations` (4 test, `track_order`) sekarang punya test nyata yang lolos. `test_*.py` di `kaji_ulang_tender`, `tnc_master_template`, `client_inquiry`, `petty_cash_entry` (folder DocType di `starlab_customizations`) masih stub kosong (class `IntegrationTestCase` tanpa method `test_*`, jadi 0 test jalan) — belum tersentuh. Total test yang beneran lolos di seluruh 4 app sekarang: 37 (27 `starlab_customizations` + 2 `starlab_lab_ops` + 4 `starlab_quality` + 4 `starlab_integrations`). Regresi ke DocType lama (Quotation/Work Order/Sample) sebagian besar masih TIDAK akan kedeteksi otomatis di luar yang sudah ditest.
  - **[Selesai]** `starlab_lab_ops/tests/test_sanity.py` yang dulu diletakkan di folder salah (di luar `frappe.get_app_path`, jadi tidak pernah ke-discover `bench run-tests`) sudah dipindah ke `starlab_lab_ops/starlab_lab_ops/starlab_lab_ops/tests/` dan sekarang benar-benar jalan (lihat Bagian 3.23c).
- **Dashboard**: beberapa metrik TSD (saldo kas real-time, conversion rate, histori klien) butuh Query Report custom kalau mau benar-benar akurat — saat ini sengaja tidak dibuatkan Number Card supaya tidak menampilkan angka yang menyesatkan.
- **`docker/apps.json`**: URL untuk `starlab_lab_ops` masih pakai repo lama (`alvirarisky/starlab_lab_ops.git`) yang menurut GitHub sendiri sudah "moved" ke `starlab_ERP.git`. Masih jalan (GitHub redirect otomatis), tapi lebih rapi kalau nanti diarahkan langsung ke URL kanonik.

---

## 7. Panduan Testing per Fitur

Semua contoh di bawah pakai `bench --site <NAMA_SITE> console < nama_file.py` (piped, bukan paste interaktif — lebih stabil). Login Desk manual bisa juga, lihat catatan di tiap bagian.

### 7.1 Client Inquiry → Kaji Ulang Tender → auto-Quotation
1. Buat Client Inquiry baru (isi Customer kalau mau lihat happy path, atau kosongkan buat cek graceful-degrade).
2. Jalankan Workflow "Ajukan" (role Marketing).
3. Buat Kaji Ulang Tender baru, isi `client_inquiry`, `rekomendasi = Layak`.
4. Cek: Client Inquiry otomatis pindah status ke "Disetujui MT"; kalau Customer terisi & Company default ada, Quotation Draft baru otomatis muncul (cek field `client_inquiry` di Quotation itu).
5. Kalau Customer kosong: cek Comment di Client Inquiry berisi pesan "Quotation Draft tidak dibuat otomatis...".

### 7.2 Quotation — kalkulasi harga & TNC
1. Buat Quotation baru, `quotation_to = Customer`, isi minimal 1 baris `parameter_detail`.
2. Isi `discount_percent`/`biaya_kirim`/`ppn_percent`, Save.
3. Cek `sub_total`/`dpp`/`total_invoice` terhitung otomatis sesuai urutan Sub Total → Discount → DPP → PPN → Biaya Kirim.
4. Cek `tnc_template` otomatis terisi versi TNC yang berlaku saat `transaction_date`.
5. Approve Quotation (jalankan semua tahap Workflow sampai Approved), lalu coba ubah `transaction_date` — `tanggal_kadaluwarsa` seharusnya TIDAK berubah lagi (guard docstatus).

### 7.3 Petty Cash Entry — workflow & Journal Entry
1. Login sebagai user role Administrasi, buat Petty Cash Entry baru, isi nominal + bukti.
2. Jalankan "Ajukan" → status jadi Menunggu Approval.
3. Login sebagai user role Direksi, jalankan "Setujui".
4. Cek: `disetujui_oleh` otomatis terisi; field `journal_entry` terisi nama Journal Entry baru (kalau akun GL & Cost Center sudah ada) ATAU muncul Comment "Journal Entry gagal dibuat otomatis..." (kalau belum, ini NORMAL untuk site yang belum full Setup Wizard).
5. Coba edit `nominal` setelah Disetujui — harus ditolak ("tidak bisa diubah lagi").

### 7.4 Document Master — siklus revisi
1. Login sebagai user salah satu dari 7 role (misal Laboratorium), buat Document Master baru dengan `owner_division = Laboratorium`.
2. Jalankan "Ajukan" (harus berhasil karena Laboratorium = pemilik dokumen ini; coba divisi lain untuk lihat ditolak).
3. Login sebagai Manajer Mutu, jalankan "Setujui".
4. Login sebagai Direksi, jalankan "Terbitkan" → status jadi Aktif, cek Riwayat Revisi bertambah 1 baris.
5. Login sebagai Manajer Mutu, jalankan "Mulai Revisi" → status Dalam Revisi, lalu ulangi siklus Ajukan→Setujui→Terbitkan → cek `edisi_revisi` naik & Riwayat Revisi bertambah baris kedua.
6. Cek permission: login sebagai role yang TIDAK didistribusikan ke dokumen ini — harusnya tidak muncul di list (`frappe.get_list` scoped, bukan `frappe.get_doc` langsung yang tidak enforce permission).

### 7.5 Sales Invoice & LHU
1. Buat LHU dengan status "Issued" (via Desk, isi Work Order + minimal 1 baris Daftar Hasil Uji).
2. Buka LHU itu, klik tombol "Buat Invoice".
3. Cek: kalau belum ada Invoice untuk LHU ini, terbuka form Sales Invoice BARU (belum tersimpan) dengan Customer/Work Order/LHU sudah terisi — lengkapi item & harga manual lalu Save.
4. Klik "Buat Invoice" lagi dari LHU yang sama — harusnya langsung diarahkan ke Invoice yang SAMA (bukan bikin duplikat).

### 7.6 Dashboard & Number Card
1. Desk → search "Dashboard [Nama Role]" (misal "Dashboard Direksi").
2. Cek semua Number Card menampilkan angka (0 kalau memang belum ada data, bukan error).
3. Cek chart tren di bawahnya render tanpa error.

### 7.7 Notifikasi
1. Pastikan minimal ada 1 user per role (lihat panduan bikin user test yang sudah dikirim sebelumnya di chat).
2. Trigger salah satu transisi approval (misal Quotation "Ajukan") — cek Error Log TIDAK ada entri "Gagal mengirim notifikasi email" kalau Email Account sudah dikonfigurasi; kalau belum, itu NORMAL (notifikasi di-skip, bukan bikin transisi gagal).
3. Jalankan scheduled job manual untuk tes cepat tanpa nunggu jadwal harian:
   ```python
   from starlab_customizations.tasks import check_invoice_due, check_invoice_overdue
   from starlab_lab_ops.tasks import check_sample_deadline_mendekat, check_sample_deadline_terlewat, check_sample_retensi
   check_invoice_due(); check_invoice_overdue()
   check_sample_deadline_mendekat(); check_sample_deadline_terlewat(); check_sample_retensi()
   ```

### 7.8 WhatsApp Settings & Client Portal
1. Desk → search "WhatsApp Settings" — cek default `enabled = 0`.
2. `/status-klien` — akses sambil login sebagai Administrator (belum terhubung ke Customer manapun) → harus muncul pesan "Akun Anda belum terhubung ke data Customer manapun".
3. Untuk tes penuh: buat User baru, tambahkan sebagai "Portal User" di salah satu Customer (tab Portal Users di form Customer), login pakai user itu, akses `/status-klien` → harus muncul list LHU & Invoice milik Customer tersebut saja.

### 7.9 Report akses Finance
1. Login sebagai user role Finance (bukan System Manager).
2. Desk → cari report "Accounts Receivable" dan "Bank Reconciliation Statement" — harus muncul di hasil pencarian & bisa dibuka (sebelumnya digembok ke Accounts Manager/User saja).

### 7.10 4 gap dari dokumen asli SAI (commit `53d85bb`)

**a. Quotation auto-numbering**
1. Quotation baru → New, isi `Quotation To = Customer` + Customer apa saja, isi minimal 1 baris `Parameter Detail` (parameter, frekuensi, qty per titik, harga satuan).
2. Save (tidak perlu submit) — cek nama dokumen berbentuk `Quo-SAI/[bulan-romawi]/[tahun]/[no-urut]`, contoh `Quo-SAI/VII/2026/001` kalau dibuat Juli 2026.
3. Buat Quotation kedua dengan cara sama di tahun yang sama — nomor urut harus naik +1 dari yang pertama.
4. (Opsional) Ganti `Transaction Date` ke bulan lain sebelum Save → angka romawi bulan ikut berubah (Januari = I, Desember = XII).

**b. TNC Master Template**
1. Desk → cari "TNC Master Template".
2. Cek ada record `Versi Template = 01`, `Berlaku Sejak = 2022-11-14`.
3. Buka record-nya, field `Konten TNC` harus berisi 12 poin S&K asli (bukan kosong).

**c. Document Distribution — MK3 & Eksternal**
1. Buka Document Master apa saja → tambah baris baru di child table Distribusi.
2. Dropdown **Divisi** harus menampilkan 9 opsi: Direksi, MM, MT, Laboratorium, Administrasi, Finance, Marketing, **MK3**, **Eksternal**.
3. Pilih "MK3" atau "Eksternal", isi Tanggal Distribusi, Save — tidak boleh ada error validasi.

**d. Laporan Keuangan Operasional — Saldo Kas Kecil**
1. Desk → jalankan report "Laporan Keuangan Operasional" tanpa filter.
2. Cek kolom baru **Saldo Kas Kecil** di paling kanan.
3. Baris kategori "Petty Cash" → Saldo kosong (by design — bukan mutasi buku besar).
4. Baris kategori "Entri Jurnal" → Saldo terisi angka running balance, urut sesuai tanggal.
5. (Opsional) Buat Petty Cash Entry baru → approve sampai "Disetujui" (trigger auto Journal Entry) → jalankan ulang report → baris "Entri Jurnal" baru muncul dengan Saldo ter-update.

**Verifikasi cepat lewat console** (tanpa lewat UI):
```python
frappe.get_meta("Document Distribution").get_field("divisi").options
frappe.db.exists("TNC Master Template", {"versi_template": "01"})
```

### 7.11 Finance read-only, 7 Workspace, histori LHU klien (commit setelah `53d85bb`)

**a. Finance tidak bisa approve Quotation**
1. Login sebagai user role Finance saja (tanpa role approval lain).
2. Buka Quotation manapun yang sedang "Menunggu Approval MT/MM/Marketing/Direksi" — tidak boleh ada tombol aksi Workflow (Setujui/Tolak) yang muncul buat Finance.
3. Coba edit field apapun di Quotation itu — harus read-only/tidak bisa Save (Custom DocPerm Finance: write=0).
4. Jalankan test otomatis: `bench --site <NAMA_SITE> run-tests --app starlab_customizations --module starlab_customizations.starlab_customizations.tests.test_quotation_workflow_permission`.

**b. 7 Workspace per role**
1. Login sebagai user dengan salah satu dari 7 role (misal Manajer Mutu) — di sidebar Desk kiri (app switcher/workspace list) harus muncul Workspace "Manajer Mutu" berisi Ringkasan (Number Card), Tren (Chart), dan Pintasan (Shortcut DocType terkait).
2. Login sebagai user dengan role LAIN (misal Marketing) — Workspace "Manajer Mutu" TIDAK boleh muncul di listnya (dibatasi lewat `roles` child table).
3. Kalau mau nambah/ubah Workspace ini ke depan: edit file di `starlab_customizations/starlab_customizations/workspace/<slug>/<slug>.json` langsung, JANGAN lewat fixtures (lihat catatan di Bagian 3.19).

**c. Histori LHU Klien di Quotation**
1. Buka Quotation dengan `Quotation To = Customer` yang punya minimal 1 LHU ber-status apapun.
2. Cek child table baru **Histori LHU Klien** di form Quotation — harus terisi otomatis (read-only) dengan daftar LHU milik Customer tersebut, terurut dari yang terbaru.
3. Terbitkan LHU baru untuk Customer yang sama, lalu refresh/buka ulang Quotation-nya — baris baru harus otomatis muncul (field ini fetch live tiap form dibuka, bukan snapshot statis).

### 7.12 Kanban Board, kop surat, icon Workspace, default filter shortcut

**a. Kanban Board**
1. Buka List View **Sample** atau **Work Order Pengujian** → klik ikon switch view → pilih **Kanban**.
2. Board "Sample per Status" / "Work Order Pengujian per Status" harus muncul dengan kolom sesuai opsi Select `status` DocType itu (Sample: Diterima/Sedang Diuji/Divalidasi/Diarsipkan/Dimusnahkan; WO: Draft/Approved/In Progress/Completed/Cancelled).

**b. Kop surat resmi**
1. Cetak Quotation apapun lewat Print Format "Quotation Ringkasan Harga" — kop surat "PT STARLAB ANALITIK INDONESIA" + alamat + telepon + email + KAN LP-2063-IDN harus muncul di paling atas (sebelumnya tidak ada kop surat sama sekali).
2. Cetak LHU apapun lewat Print Format "LHU Resmi" — kop surat yang SAMA (bukan lagi placeholder "[LOGO PLACEHOLDER]"/"Jl. Contoh Alamat Placeholder") harus muncul, dan baris kota di tanda tangan sudah "Bogor" (bukan "Kota Placeholder").
3. Desk → cari "Letter Head" → record "PT Starlab Analitik Indonesia" harus ada dengan `Is Default` tercentang.

**c. Icon Workspace**
1. Login, lihat sidebar/App Switcher Desk — 7 Workspace role harus punya icon berbeda-beda (bukan briefcase semua). Kalau ternyata masih sama semua di instance yang dites, jalankan `bench migrate` dulu di instance itu — datanya sudah benar di fixture/module file, cuma belum ke-sync ke DB instance tersebut.

**d. Default filter shortcut**
1. Login sebagai Direksi, buka Workspace Direksi, klik shortcut "Quotation" — List View yang terbuka harus otomatis ke-filter `Workflow State = Menunggu Approval Direksi` (bukan nampilin semua Quotation).
2. Login sebagai Manajer Teknis, klik shortcut "Quotation" di Workspace-nya — harus ke-filter `Workflow State = Menunggu Approval MT`.
3. Workspace Manajer Mutu: pastikan TIDAK ada lagi shortcut "Document Distribution" (sudah dihapus karena tidak pernah bisa dibuka).

### 7.13 Client Dashboard tanpa login & Marketing bukan approver (commit setelah `a26a97f`)

**a. Client Dashboard tanpa login**
1. Buka `/tracking` di browser **tanpa login sama sekali** (mode incognito juga boleh) — halaman harus tampil normal, TIDAK redirect ke `/login`.
2. Masukkan nomor Quotation atau Work Order yang valid → klik "Cek Status" — harus muncul status pekerjaan (dan status/tautan unduh LHU kalau sudah terbit), TANPA menampilkan harga/nominal apa pun.
3. Masukkan nomor yang tidak ada → harus muncul pesan "tidak ditemukan", bukan error.
4. `/status-klien` (versi login) tetap bisa diakses seperti biasa oleh user dengan Portal User terdaftar — tidak berubah.

**b. Marketing bukan approver Quotation**
1. Login sebagai user role Marketing saja (tanpa role approval lain) — buka Quotation manapun yang sedang "Menunggu Approval MT/MM/Direksi": tidak boleh ada tombol Workflow Action (Setujui/Tolak) yang muncul.
2. Coba edit field apapun di Quotation itu sebagai Marketing — harus read-only/tidak bisa Save.
3. Cek Role List (Desk → Role) dan daftar Employee — role "Marketing" dan Employee dengan Designation Marketing harus **masih ada**, tidak terhapus.
4. Login sebagai Marketing, buka Workspace "Marketing" → shortcut "Quotation" — sekarang nampilin semua Quotation (tanpa filter state tertentu, karena Marketing tidak lagi punya approval queue).
5. Jalankan test otomatis: `bench --site <NAMA_SITE> run-tests --app starlab_customizations --module starlab_customizations.starlab_customizations.tests.test_quotation_workflow_permission` — harus 4 test lolos (2 Finance, 2 Marketing).

### 7.14 PRD v8 Sprint 12 — Penyesuaian Quotation (lihat Bagian 3.22)

**a. Reset penuh approval saat konten diubah pasca-approval sebagian**
1. Buat Quotation baru (via Client Inquiry), approve sampai state "Menunggu Approval MM" (login sebagai Manajer Teknis, klik "Setujui").
2. Login sebagai Manajer Mutu, buka Quotation itu → ubah `Discount Percent` atau baris Parameter Detail apapun → Save (jangan klik tombol Workflow Action).
3. Cek state Quotation — harus balik ke "Menunggu Approval MT", BUKAN tetap "Menunggu Approval MM".
4. Ulangi sampai state "Menunggu Approval Direksi", ubah konten lagi sebagai Direksi → harus tetap reset PENUH ke "Menunggu Approval MT" (bukan mundur satu tahap ke MM).
5. Sebagai kontrol: save Quotation di state manapun TANPA mengubah konten apa pun — state tidak boleh berubah.

**b. Expiry 45 hari + state Kedaluwarsa + Aktifkan Kembali**
1. Buat Quotation baru → cek field `Tanggal Kadaluwarsa` = `Transaction Date` + 45 hari (bukan 30).
2. Approve Quotation sampai "Approved", lalu set `Tanggal Kadaluwarsa` manual ke tanggal lampau (lewat Desk atau `bench console`) → jalankan `bench --site <NAMA_SITE> execute starlab_customizations.tasks.check_quotation_expiry` → state harus berubah jadi "Kedaluwarsa".
3. Buka Quotation yang sudah "Kedaluwarsa" → harus ada tombol Workflow Action "Aktifkan Kembali" (role Administrasi) → klik → state balik ke "Approved" dan `Tanggal Kadaluwarsa` diperpanjang 45 hari dari hari ini.

**c. `client_inquiry` wajib**
1. Coba buat Quotation manual dari Desk tanpa mengisi field "Referensi Form A" (`client_inquiry`) → Save harus gagal dengan error field wajib.
2. Isi field itu dengan Client Inquiry yang valid → Save harus berhasil.

**d. Field `tingkat_percepatan`**
1. Buka Quotation manapun (state Draft) → set `Tingkat Percepatan` ke "5 Hari Kerja (+100%)" → Save → cek `Rush Fee Hari` = 5, `Rush Fee Percent` = 100 (otomatis terisi).
2. Ganti ke "7 Hari Kerja (+80%)" → cek `Rush Fee Hari` = 7, `Rush Fee Percent` = 80.
3. Ganti ke "Normal" → kedua field rush fee harus kosong/0.
4. Ganti ke "Lainnya (Input Manual)" → isi `Rush Fee Hari`/`Rush Fee Percent` manual → Save → nilai manual harus tetap tersimpan apa adanya (tidak ditimpa otomatis).

**e. Konsolidasi `kategori_pelanggan`**
1. Buka DocType Customer di Desk → cek field "Jenis Industri" sudah tidak ada lagi di form.
2. Field "Kategori Pelanggan" tetap ada dengan opsi baku (Perusahaan, Individu-Perorangan, Institusi Pemerintah, Universitas-Sekolah, Lain-lain).
3. Untuk Customer lama yang sebelumnya cuma punya `jenis_industri` terisi (bukan `kategori_pelanggan`) — cek nilainya sudah otomatis pindah ke `kategori_pelanggan` setelah `bench migrate` (patch jalan sekali saat migrate).

**f. T&C v02**
1. Buka menu "TNC Master Template" → harus ada record baru `Versi Template = 02` dengan `Konten TNC` menyebutkan "45 hari" dan pelunasan "7 (tujuh) hari kalender".
2. Record `Versi Template = 01` yang lama TIDAK berubah (masih menyebutkan "30 hari").
3. Buat Quotation baru → field `TNC Template` yang terisi otomatis harus menunjuk ke versi `02`.

**g. Sales Invoice due date**
1. Buat Sales Invoice baru (draft), isi `Posting Date` = hari ini → Save → cek `Due Date` = `Posting Date` + 7 hari.
2. Buat Sales Invoice lain dengan `Posting Date` mundur/backdated (perlu centang "Set Posting Time" di Desk) → cek `Due Date` tetap konsisten `Posting Date` + 7 hari.

**h. Jalankan seluruh test otomatis**
```
bench --site <NAMA_SITE> run-tests --app starlab_customizations
```
Saat ditulis (sebelum Bagian 3.23 rush fee menambah 3 test lagi), harus 24 test lolos, mencakup semua poin a–g di atas (file: `test_quotation_revision_and_expiry.py`, `test_quotation_fields.py`, `test_sales_invoice_due_date.py`, plus `test_quotation_workflow_permission.py` yang direfactor pakai helper baru `quotation_test_utils.py`). Lihat Bagian 7.15h untuk angka terbaru (27 test).

### 7.15 Rush fee di Total Invoice, TODO SLA dibersihkan, test coverage baru (lihat Bagian 3.23)

**a. Rush fee masuk Total Invoice**
1. Buat Quotation baru, isi minimal 1 baris Parameter Detail dengan harga > 0.
2. Set `Tingkat Percepatan` = "5 Hari Kerja (+100%)" → Save.
3. Cek field baru `Rush Fee (Nominal)` (`rush_fee_amount`) terisi = `Sub Total x 100%` (sama dengan Sub Total).
4. Cek `Total Invoice` naik dibanding sebelum tier diisi (ikut menghitung rush fee).
5. Set `Discount (%)` ke suatu angka > 0 → cek potongan Discount di Print Format "Quotation Ringkasan Harga" menghitung dari (Sub Total + Rush Fee), bukan Sub Total saja — **ini bagian yang masih ASUMSI, laporkan ke PO kalau ternyata seharusnya beda**.
6. Cetak Print Format "Quotation Ringkasan Harga" → baris "Rush Fee" harus muncul (karena nilainya > 0), lengkap dengan catatan kecil soal status ASUMSI di bagian bawah.
7. Set `Tingkat Percepatan` balik ke "Normal" di Quotation lain (atau yang baru) → cetak Print Format lagi → baris "Rush Fee" harus TIDAK muncul sama sekali.

**b. Document Master workflow (test otomatis baru)**
```
bench --site <NAMA_SITE> run-tests --app starlab_quality
```
Harus 4 test lolos: siklus Draft→Menunggu Approval MM→Menunggu Approval Direksi→Aktif, tolak di MM dengan/tanpa `catatan_revisi`, dan test yang mengunci bahwa status "Usang" tidak punya jalur otomatis (lihat catatan keputusan PO di Bagian 3.23).

**c. `starlab_lab_ops` sanity test (sekarang benar-benar jalan)**
```
bench --site <NAMA_SITE> run-tests --app starlab_lab_ops
```
Harus 2 test lolos (sebelumnya 0 karena salah folder).

**d. Client Dashboard `track_order` (test otomatis baru)**
```
bench --site <NAMA_SITE> run-tests --app starlab_integrations
```
Harus 4 test lolos: akses guest tanpa login, response tanpa field harga/finansial, rate-limit 30 request/60 detik benar-benar memblokir permintaan ke-31, dan nomor pesanan tidak ditemukan mengembalikan `{"found": false}`.

**e. Jalankan seluruh 4 app sekaligus**
```
bench --site <NAMA_SITE> run-tests --app starlab_customizations
bench --site <NAMA_SITE> run-tests --app starlab_lab_ops
bench --site <NAMA_SITE> run-tests --app starlab_quality
bench --site <NAMA_SITE> run-tests --app starlab_integrations
```
Total 37 test lolos (27 + 2 + 4 + 4).

### 7.16 Polish Client Dashboard + branding (lihat Bagian 3.24)
1. Setelah `bench migrate` (patch `set_sai_branding` jalan otomatis), login ke Desk → cek logo di pojok kiri atas navbar sekarang logo SAI (ikon bintang+LAB), bukan logo Frappe default.
2. Cek favicon tab browser juga berubah jadi logo SAI yang sama.
3. Buka `/tracking` tanpa login → cek logo SAI muncul di atas form, di atas judul "Cek Status Pesanan".
4. Klik "Cek Status" dengan input kosong-lalu-diisi → **selama loading**, harus muncul spinner berputar + teks "Mencari...", bukan cuma teks statis.
5. Masukkan nomor Quotation/Work Order yang valid dan punya Work Order + LHU → hasil harus tampil sebagai card terpisah per Work Order (ada border kiri warna cyan, background sedikit berbeda dari putih polos), status Work Order & LHU masing-masing pakai badge warna (ijo/kuning/merah/biru sesuai isi statusnya).
6. Masukkan nomor yang statusnya "Cancelled"/"Ditolak" (kalau ada datanya) → badge harus merah. Nomor dengan status "Completed"/"Issued"/"Disetujui" → badge hijau.
7. Buka `/tracking` di layar HP (atau resize browser ke < 480px lebar) → tombol "Cek Status" harus turun ke bawah input (stack vertikal), bukan kepotong/menyempit di samping input.
8. Cek tombol "Cek Status" warnanya cyan brand SAI (`#11A8E0`), bukan hitam/abu-abu gelap atau biru default Bootstrap — **kalau masih abu-abu/hitam, kemungkinan besar cache CSS browser, hard refresh dulu** (compiled CSS Website Theme punya nama file unik per generate, jadi seharusnya tidak butuh clear cache manual, tapi in case tetap perlu).

### 7.17 Workspace CRM & LIMS (lihat Bagian 3.25)

**Cara buka**: login ke Desk (`/app`, redirect otomatis ke `/desk`) sebagai user internal manapun (semua role bisa lihat, `roles` dikosongkan) → klik ikon Workspace picker di pojok kiri atas (atau sidebar kiri) → "CRM" dan "LIMS" akan muncul di bawah 7 Workspace role yang sudah ada. Bisa juga langsung lewat URL `/app/crm` atau `/app/lims`.

Kalau belum ada akun buat coba-coba: 7 akun test per role sudah di-seed otomatis saat `after_install` (kalau `developer_mode` aktif) lewat `starlab_integrations/seed_test_users.py` — semua pakai password `Test@12345`, contoh `direksi.test@example.com`, `marketing.test@example.com`, dst (lihat daftar lengkap `TEST_USERS` di file itu). Kalau site sudah lama ke-install sebelum patch ini ada, akun-akun ini tidak otomatis muncul (hook `after_install` cuma jalan sekali saat fresh install) — jalankan manual lewat `bench --site <NAMA_SITE> console`:
```python
import frappe
frappe.conf.developer_mode = 1
from starlab_integrations.seed_test_users import after_install
after_install()
```

**a. Workspace CRM**
1. Buka Workspace CRM → cek 7 Number Card muncul (4 Client Inquiry per status + 3 Quotation per status), angkanya masuk akal dibanding jumlah data aktual.
2. Cek chart "Corong Konversi" muncul sebagai Bar chart 3 batang menurun: Form A (Client Inquiry) → Quotation Dibuat → Quotation Approved.
3. Klik tiap pintasan (Client Inquiry, Kaji Ulang Tender, Quotation, Customer, TNC Master Template) → harus membuka List View DocType terkait, bukan error 404.
4. Login sebagai role manapun (misal `laboratorium.test@example.com`, role yang TIDAK biasanya urus Marketing/Direksi) → Workspace CRM tetap harus bisa dibuka dan terlihat isinya (visibility tidak dibatasi role) — tapi coba create/edit Quotation baru tetap harus kena aturan Role Permission normal (kalau role itu memang tidak punya izin write ke Quotation).
5. Cek 7 Workspace role lama (Direksi, Marketing, dst) masih ada semua, tidak ada yang hilang/berubah.

**b. Workspace LIMS**
1. Buka Workspace LIMS → cek 4 Number Card muncul (Sample Belum Diuji, Sample Sedang Diuji, Test Result Menunggu Validasi, LHU Draft Menunggu Diterbitkan).
2. Di bagian "Papan Kanban", klik pintasan "Sample — Kanban" → harus langsung membuka Kanban View DocType Sample dengan board "Sample per Status" aktif (kolom sesuai opsi Select `status`), bukan List View biasa.
3. Klik pintasan "Work Order Pengujian — Kanban" → sama, harus langsung ke Kanban View board "Work Order Pengujian per Status".
4. Klik 5 pintasan biasa di bagian "Pintasan" (Work Order Pengujian, Sample, Test Result, Test Parameter, LHU) → semua harus membuka List View normal.
5. Cek icon Workspace LIMS di sidebar picker beda dari icon Workspace Laboratorium (LIMS pakai `clipboard-check`, Laboratorium pakai `flask-conical`) — supaya kelihatan jelas ini dua Workspace yang berbeda, bukan duplikat.

---

## 8. Referensi Dokumen Lain
- `docs/audit-sebelum-sprint-5.md` — audit lengkap Sprint 1–4 sebelum sesi ini dimulai.
- `docs/dependency-install-order.md` — kenapa `starlab_quality` harus install sebelum `starlab_lab_ops`.
- `docs/translation-activation.md` — cara aktifkan terjemahan Bahasa Indonesia (config, bukan kode).
