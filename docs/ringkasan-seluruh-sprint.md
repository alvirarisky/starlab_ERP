# Ringkasan Pengerjaan Seluruh Sprint (Sprint 1 – 11)

**Cakupan:** Seluruh riwayat proyek ERP SAI dari Sprint 1 (Setup & Master Data) sampai `starlab_integrations` (TSD Sprint 9 asli). Sprint 1–4 dikerjakan sebelum sesi ini (ringkasan diambil dari `docs/audit-sebelum-sprint-5.md`); Sprint 5–11 dikerjakan dalam sesi ini, commit `6b067cd` sampai `8b988ff` di branch `develop`.

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

---

## 4. Keputusan yang Sudah Ditentukan (PO Decisions)

| # | Topik | Keputusan | Alasan/Konteks |
|---|---|---|---|
| 1 | Status "Fase 2" (Test Result, LHU, Petty Cash, Document Control) | Dianggap selesai/delivered, bukan prioritas ulang — polish hanya kalau memang sedang disentuh | Sudah fungsional dari sebelum Sprint 5, tinggal dipoles |
| 2 | Auto-numbering Quotation | Tetap default ERPNext, JANGAN hardcode format final SAI | PRD v6 Open Question #5 belum dijawab Administrasi |
| 3 | Client Inquiry (Form A) | Opsional, bukan satu-satunya jalan bikin Quotation | Administrasi tetap bisa bikin Quotation manual |
| 4 | Lampiran A1 | Field attach/update sederhana di Quotation, bukan DocType/Workflow terpisah | Simplifikasi scope |
| 5 | Dual approval Petty Cash Entry | Disederhanakan: Direksi saja (bukan Direksi+Finance) | Keputusan eksplisit setelah ditanya |
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
| Format auto-numbering Quotation | `starlab_customizations/quotation_hooks.py` (komentar TODO di baris atas) | Administrasi konfirmasi format resmi (`Quo-SAI/[bulan romawi]/[tahun]/[no]` dari BRA/PRD), baru diimplementasikan |
| Rush fee Quotation | Field `rush_fee_hari`/`rush_fee_percent` sudah ada, belum masuk kalkulasi | PRD v6 Open Question #10 perlu dijawab dulu |
| Target eskalasi SLA Quotation | `starlab_customizations/tasks.py::check_quotation_sla` | PRD v6 Open Question #1 — sekarang default "reminder ulang ke approver yang sama", ganti kalau ternyata harus ke atasan |
| WhatsApp Settings | Desk → cari "WhatsApp Settings" | Isi provider, API URL, API Key, Nomor Pengirim begitu sudah pilih & daftar provider (Fonnte/Twilio/WhatsApp Business API), lalu centang "Aktifkan" |
| Item master untuk Quotation/Invoice | `Quotation Parameter Detail`, tombol "Buat Invoice" di LHU | Test Parameter belum ditautkan ke Item master ERPNext — auto-create Quotation/Invoice sengaja TIDAK isi tabel `items` standar karena ini. Kalau mau full-otomatis, perlu diputuskan dulu: bikin 1 Item generik "Jasa Pengujian" atau mapping per parameter |
| LHU: status custom vs native submit | `starlab_lab_ops` — LHU sudah punya Custom DocPerm submit/cancel/amend yang nganggur (DocType belum `is_submittable`) | Diputuskan dulu: pindah ke native submit (buang status custom Draft/Issued/Revised/Superseded) atau hapus DocPerm yang nganggur |

---

## 6. Catatan / PR untuk Kita (Follow-up)

- **Sprint 10 TSD asli (Migrasi Data, UAT, Go-Live)** — tidak bisa dikerjakan lewat sesi coding. Butuh: file data historis (Excel/Google Drive lama), staf yang benar-benar melakukan UAT per role, keputusan go-live bertahap (Quotation/WO dulu → Sample/QC → sisanya).
- **Belum ada test otomatis** — audit awal berkali-kali nge-flag ini sebagai risiko nomor satu. Semua `test_*.py` di setiap DocType masih stub kosong. Regresi ke DocType lama (Quotation/Work Order/Sample) tidak akan kedeteksi otomatis kalau ada yang ubah lagi ke depan.
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

---

## 8. Referensi Dokumen Lain
- `docs/audit-sebelum-sprint-5.md` — audit lengkap Sprint 1–4 sebelum sesi ini dimulai.
- `docs/dependency-install-order.md` — kenapa `starlab_quality` harus install sebelum `starlab_lab_ops`.
- `docs/translation-activation.md` — cara aktifkan terjemahan Bahasa Indonesia (config, bukan kode).
