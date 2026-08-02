# Laporan Audit Menyeluruh — ERP SAI (Pra-Testing)

**Tanggal audit:** 2026-08-02
**Auditor:** Claude (static + functional review)
**Lingkup:** Seluruh 4 custom app (`starlab_customizations`, `starlab_lab_ops`, `starlab_quality`, `starlab_integrations`) + konfigurasi ERPNext core yang relevan (Role, Workspace, Report, Print Format), dijalankan terhadap instance Docker lokal (`starlab.local`, container `frappe-backend-1` dkk, image `starlab-lab-ops:latest`).
**Metode:** Static review (kode, DocType JSON, fixtures, workflow) **dikombinasikan** dengan verifikasi fungsional langsung ke instance yang benar-benar hidup — permission disimulasikan per-role lewat `frappe.has_permission()` untuk 7 role custom x 26 DocType, workflow state-machine dibaca langsung dari DB, dan satu skenario bypass-workflow dicoba dieksekusi langsung di console.
**Pembanding:** Audit internal sebelumnya (`docs/audit-sebelum-sprint-5.md`, 2026-07-26) dan `docs/keputusan_bisnis_terbaru.md` (jawaban stakeholder, dikumpulkan 2026-07-30).

> **Update 2026-08-02 malam:** Semua temuan kode di bawah ini (Critical/High/Medium yang bukan soal keputusan bisnis/UX manual) **sudah diperbaiki, di-migrate, dan diverifikasi ulang live** terhadap instance yang sama. Status per-item ada di `docs/audit/CHECKLIST_TESTING.md` (ditandai ✅). Laporan di bawah ini dibiarkan apa adanya sebagai catatan kondisi SEBELUM perbaikan — untuk status terkini, rujuk checklist tersebut.

> Catatan metodologi: environment ini tidak punya browser/UI automation yang tersedia untuk saya, jadi "functional review" di sini berarti login disimulasikan lewat session Frappe asli (`frappe.set_user(...)` + `has_permission`/`get_all` dengan permission check aktif, BUKAN `ignore_permissions`) terhadap data yang benar-benar ada di database instance ini — bukan tebakan dari baca kode saja. ​Untuk verifikasi visual (layout rusak, print PDF terlihat rapi, dsb.), silakan tim tetap lakukan pengecekan mata langsung di browser besok; itu di luar apa yang bisa saya konfirmasi dari sini.

---

## Ringkasan Eksekutif

**Kondisi umum: cukup solid untuk fondasi bisnis-proses-nya (DocType, Workflow, dan sebagian besar RBAC sudah konsisten dan masuk akal), tapi ada beberapa temuan Critical yang sebaiknya diperbaiki atau minimal diketahui semua orang SEBELUM sesi testing besok dimulai** — dua di antaranya adalah bug yang sudah punya jawaban resmi dari stakeholder tapi belum dieksekusi ke kode, satu lagi berpotensi membuat seluruh sesi testing role Direksi/Administrasi jadi tidak representatif kalau memakai akun test yang salah.

Dibanding audit internal sebelumnya (26 Juli), progress signifikan: `starlab_quality` sekarang punya fixtures + workflow + row-level permission (sebelumnya nol sama sekali), `starlab_integrations` sudah terisi penuh (WhatsApp gateway + Client Portal — sebelumnya app kosong), Client Inquiry/Kaji Ulang Tender/TNC Master Template sudah ada. Ini progress nyata, bukan cuma menu kosong.

**Risk level keseluruhan: MEDIUM-HIGH**, didorong terutama oleh 2 temuan yang **sudah** punya keputusan bisnis tertulis tapi kodenya belum disesuaikan (bukan soal "belum tahu maunya apa", tapi "sudah tahu, belum dikerjakan") — ini yang paling gampang untuk salah kaprah kalau testing besok berjalan tanpa fix ini, karena test akan "lolos" secara fungsional tapi sebenarnya menguji formula/RBAC yang sudah diketahui salah.

**Ringkasan angka temuan:**

| Severity | Jumlah | Kategori dominan |
|---|---|---|
| Critical | 5 | Kalkulasi finansial vs keputusan bisnis, RBAC vs keputusan bisnis, integritas akun test, client portal |
| High | 5 | Report tidak accessible, endpoint tanpa guard, delete pada data yang sudah approved, git hygiene patch fix |
| Medium | 6 | Self-approval structural, audit-trail bypass, menu domain tanpa role restriction, field tidak aktif |
| Low | 4 | Teks caveat internal bocor ke print klien, dokumentasi field stale, clutter Role Profile bawaan |

**Go/No-Go: lihat Bagian 6 di akhir laporan** — ringkasnya: **Go dengan syarat**, testing besok tetap bisa jalan, tapi 3 item Critical (Rush Fee, akses Bank Direksi, akun test ganda) sebaiknya di-fix atau minimal diumumkan eksplisit ke tim tester pagi ini juga, supaya hasil testing besok tidak "false positive".

---

## Bagian 1 — Peta Role, Role Profile, dan Akun Test

### 1.1 Role yang ditemukan

7 Role custom (semua `desk_access: 1`, terdaftar di `starlab_customizations/starlab_customizations/fixtures/role.json` dan tervalidasi ada di DB live):

| Role | Representasi divisi |
|---|---|
| Direksi | Direktur / manajemen puncak |
| Manajer Teknis | Kepala teknis lab |
| Manajer Mutu | Quality Manager (ISO 17025) |
| Finance | Keuangan |
| Marketing | Sales/CRM |
| Administrasi | Admin/ops |
| Laboratorium | Analis/penyelia lab |

Plus role bawaan yang relevan: `Customer` (client portal, `desk_access: 0`), `System Manager`/`Administrator` (superuser teknis), dan ~40 role bawaan ERPNext lain (Accounts Manager, HR Manager, Sales Manager, dst.) yang **tidak dipakai** oleh custom role manapun tapi tetap ada di sistem (lihat temuan Efisiensi E-4).

**Role Profile** (`Purchase`, `Sales`, `Accounts`, `Manufacturing`, `Inventory`) — 5 Role Profile bawaan ERPNext masih ada tapi **tidak dipakai satupun** oleh user manapun di sistem (`role_profile_name` semua user = `None`). Bukan bug, tapi kandidat cleanup (lihat E-4).

### 1.2 Akun test yang ada di database — TEMUAN CRITICAL (C-3)

Ditemukan **dua generasi akun test** hidup berdampingan di database instance ini:

| Set | Contoh | Dibuat | Role aktual |
|---|---|---|---|
| **Resmi** (`seed_test_users.py`, `after_install` hook, guarded `developer_mode`) | `direksi.test@example.com`, `finance.test@example.com`, dst. (7 akun) | 2026-07-29, oleh Administrator, otomatis | **Hanya 1 role bisnis** + role bawaan (`All`, `Guest`, `Desk User`) — bersih |
| **Lama/manual** (tidak ada di kode manapun — hanya ada di data live) | `test.direksi@starlab.local`, `test.administrasi@starlab.local`, dst. (7 akun) + `tester@starlab.local` | 2026-07-26, oleh Administrator, manual | **Role bisnis DITUMPUK dengan `System Manager` + `Accounts User`** |

Contoh nyata dari query live: `test.direksi@starlab.local` punya role `['Direksi', 'System Manager', 'Accounts User', 'All', 'Guest', 'Desk User']` — bukan cuma Direksi.

**Kenapa ini Critical untuk besok:** kalau tester manapun login pakai akun `test.*@starlab.local` untuk "menguji sebagai role X", hasil ujinya **tidak valid** — akun itu efektif adalah admin (System Manager melihat/mengubah SEMUA doctype tanpa batas, termasuk yang harusnya dibatasi RBAC-nya), sehingga bug RBAC yang harusnya kelihatan (mis. role X tidak boleh lihat Y) justru tidak akan pernah muncul karena akun test-nya sendiri sudah py-pass semua pembatasan. Ini persis skenario "test lolos padahal fitur yang diuji rusak".

**Rekomendasi:** pakai **hanya** akun `*.test@example.com` (password `Test@12345`, sesuai `seed_test_users.py`) untuk seluruh sesi role-play besok. Pertimbangkan menghapus atau menonaktifkan 7 akun `test.*@starlab.local` + memastikan `tester@starlab.local` (yang juga cuma `System Manager`, tanpa role bisnis apapun — dipakai untuk workspace dev privat "Starlab Lab Ops") tidak disalahgunakan sebagai representasi role bisnis manapun.

### 1.3 Home page routing per role

`starlab_customizations/starlab_customizations/install.py` memetakan 7 role → Workspace dengan nama sama persis (`ROLE_HOME_WORKSPACE`, baris 20-28), dikonfirmasi cocok 1:1 dengan 7 file Workspace JSON yang ada. Kalau user punya lebih dari satu role custom sekaligus, landing page-nya mengikuti urutan `frappe.get_roles()` yang **tidak eksplisit dikontrol** (non-deterministic secara desain) — bukan bug untuk kondisi normal (satu user = satu role bisnis, sesuai desain seed), tapi catat kalau ke depan ada user dengan multi-role bisnis.

---

## Bagian 2 — Matriks Role x DocType x Permission (terverifikasi live)

Diambil langsung dari instance hidup dengan mensimulasikan session tiap role (`frappe.has_permission()`, bukan cuma baca fixture JSON — jadi ini sudah mencerminkan efek gabungan DocPerm bawaan + Custom DocPerm + hook permission tambahan). `export` selalu mengikuti `read` di sistem ini (pola konsisten di semua fixture) sehingga tidak ditulis ulang di kolom; kolom di bawah adalah singkatan dari read(**R**)/write(**W**)/create(**C**)/delete(**D**)/submit(**S**)/cancel(**X**).

| DocType | Direksi | Marketing | Administrasi | Finance | Laboratorium | Manajer Teknis | Manajer Mutu |
|---|---|---|---|---|---|---|---|
| Quotation | R W S X | R | R W C D **S** | R | — | R W | R W |
| Client Inquiry | R | R W C | R | — | — | R W | — |
| Kaji Ulang Tender | R | R | R | — | — | R W C | — |
| Petty Cash Entry | R W | — | R W C **D** | R | — | — | — |
| TNC Master Template | R | R | R W C | R | — | R | R |
| Sales Invoice | R **X** | R | R W C **D S** | R W C S **X** | — | — | — |
| Customer | R | R | R | R | — | R | R |
| Bank Account/Transaction/Reconciliation/Statement Import | **—** | — | — | R W C | — | — | — |
| Work Order Pengujian | R W | R | R W C | R | R W | R W | — |
| Sample | R | R | R W C | R | R W C | R W | — |
| Test Result | R | — | — | — | R W C **D** | R W | — |
| LHU | R **X** | R | R W C | R | R | R | R W C **S X** |
| Document Master | R W C | R W C | R W C | R W C | R W C | R W C | R W C **D** |
| Test Parameter, QC Detail, WO Parameter Detail | — | — | — | — | — | — | — |
| Payment Entry, Journal Entry, GL Entry, Employee, Warehouse | — | — | — | — | — | — | — |

*(sel kosong "—" = tidak ada akses sama sekali termasuk read)*

**Temuan langsung dari matriks ini** (detail severity di Bagian 4):

- **Baris Bank Account/Transaction/dkk: Direksi = "—" (kosong total)** meski keputusan bisnis 2026-07-30 poin 9 eksplisit bilang "Finance **dan** Direksi" yang boleh akses Rekening Koran/Mutasi Kas → **C-2, Critical**.
- **Quotation: Administrasi punya `submit` mentah** meski secara Workflow submit final semestinya cuma terjadi di ujung rantai approval (Direksi) → **C-4, Critical, perlu verifikasi manual**.
- **Petty Cash Entry / Test Result / Document Master: delete diberikan ke role yang juga bisa create-nya**, dan ketiga DocType ini **bukan submittable** (tidak ada proteksi docstatus) → **H-2, High**.
- Tidak satupun DocType/Custom DocPerm di seluruh sistem memakai **field-level permission** (`permlevel > 0`) — dikonfirmasi 0 baris di semua app. Ini bukan otomatis salah (tidak ada field "harga pokok/margin/gaji" di skema Quotation — hanya harga jual, jadi tidak ada yang perlu digembok di level field), tapi dicatat sebagai fakta arsitektur: kalau ke depan ada field sensitif baru, harus diingat mekanisme ini belum pernah dipakai sama sekali di codebase ini.

---

## Bagian 3 — Temuan per Role

### Direksi
Representasi eksekutif — akses baca luas ke hampir semua modul bisnis (Quotation, Petty Cash, LHU, Document Master, Sales Invoice), plus wewenang final approval (Setujui di ujung rantai Quotation/Petty Cash/Document Master) dan `cancel` di beberapa dokumen (Quotation, Sales Invoice, LHU). **Gap:** nol akses ke data perbankan (C-2). Cukup masuk akal Direksi bisa `cancel` LHU resmi (override eksekutif), tapi ini sebaiknya dikonfirmasi sengaja (M-1).

### Marketing
Akses sesuai fungsi (create Client Inquiry, read Quotation/Sample/LHU, sedikit ke Document Master). Tidak over-permission. Satu hal yang perlu dikonfirmasi: Marketing punya `write+create` di Document Master (dokumen mutu terkendali) — sesuai desain `ROLE_BY_DIVISION_CODE` di `document_control_hooks.py` (setiap divisi boleh ajukan dokumennya sendiri), jadi ini kemungkinan besar disengaja, bukan bug (M-3).

### Administrasi
Role dengan cakupan create/write terluas (Quotation, Sales Invoice, Petty Cash, Work Order, Sample, LHU, TNC Template) — sesuai posisinya sebagai hub operasional/admin di TSD. **Temuan:** DocPerm `submit` mentah di Quotation (C-4) dan `delete` di Petty Cash Entry/Sales Invoice yang sudah tidak lagi Draft (H-2).

### Finance
Akses penuh ke Sales Invoice + data perbankan, read-only ke Quotation/Petty Cash/Document Master. Ini role paling konsisten dengan tanggung jawabnya. Satu gap fungsional: **tidak ada akses ke Payment Entry/Journal Entry/GL Entry** sama sekali (kosong untuk semua role, bukan cuma Finance) — kalau Finance memang perlu input pembayaran langsung (bukan lewat auto-JE dari Petty Cash/Invoice), ini gap yang perlu dikonfirmasi tim (M-6).

### Laboratorium
Akses sesuai fungsi teknis harian (Sample, Work Order, Test Result — create+write), read-only ke LHU (LHU final cuma Manajer Mutu yang submit, ini benar secara desain integritas laporan resmi). **Temuan:** `delete` di Test Result (H-2) — analis bisa hapus hasil uji yang sudah pernah diajukan validasi.

### Manajer Teknis
Approval tahap pertama Quotation & Work Order, validasi Test Result. Konsisten dengan tanggung jawab teknis. Tidak ada temuan RBAC signifikan spesifik role ini di luar yang sudah dicatat di level sistem.

### Manajer Mutu
Kontrol penuh Document Master (termasuk `delete` — H-2) dan submit/cancel LHU final. Sesuai posisinya sebagai pemilik proses ISO 17025, tapi `delete` pada dokumen mutu yang sudah "Aktif" tetap perlu dipikirkan ulang untuk kepatuhan retensi rekaman.

### Customer (Client Portal)
**Temuan Critical (C-5):** LHU tidak punya Custom DocPerm untuk role `Customer` sama sekali (cuma `System Manager`), padahal halaman portal `/status-klien` query LHU untuk user Customer tanpa `ignore_permissions=True`. Sales Invoice punya default ERPNext portal permission (aman, dipakai juga oleh `/invoices` native), tapi LHU murni custom doctype tanpa itu. Berpotensi seluruh fitur Client Portal (TSD Bagian 9) gagal total untuk user Customer manapun. **Ini WAJIB dites paling pertama besok pagi** sebelum sesi testing dimulai — lihat checklist.

Terpisah dari itu, ada endpoint **guest-accessible** `tracking.py` (`/tracking`, `track_order`) yang sengaja tanpa login (by design, dikonfirmasi lewat komentar developer sebagai keputusan PO, dimitigasi rate-limit 30 req/menit, sengaja tidak menampilkan field harga). Ini bukan bug, tapi dicatat karena berbeda model exposure dari `/status-klien` — kalau tim belum sadar 2 pintu portal ini punya level proteksi berbeda, worth dikonfirmasi ulang bahwa risk-nya masih diterima (M-7).

### System Manager / Administrator
Superuser teknis, dipakai untuk 5 laporan yang seharusnya juga bisa diakses role bisnis (H-1). Tidak ada temuan RBAC untuk role ini sendiri (memang dimaksudkan penuh akses).

---

## Bagian 4 — Temuan per Area

### 4.A — Kesesuaian Menu

**A-1 (Low/Informational).** Menu domain vs menu per-role yang terlihat "duplikat" (Finance vs Keuangan, Kualitas vs Manajer Mutu, CRM vs Marketing/Administrasi, LIMS vs Laboratorium/Manajer Teknis) **bukan duplikasi tak sengaja** — dikonfirmasi lewat struktur `parent_page` di Workspace JSON: yang satu adalah workspace "overview domain" top-level tanpa restriksi role, yang satu lagi child page role-specific bersarang di bawahnya dengan shortcut lebih sedikit/spesifik. Pola ini konsisten di 4 domain (Keuangan, Kualitas, CRM, LIMS). Bukan temuan yang perlu diperbaiki, tapi worth didokumentasikan supaya user baru tidak bingung ada 2 menu mirip.

**A-2 (Medium, M-4).** Ke-4 workspace domain (CRM, LIMS, Keuangan, Kualitas) punya `roles: []` (kosong) dan `public: 1` — artinya **semua role melihat ke-4 menu domain ini di sidebar**, termasuk yang isinya lintas-divisi (mis. Laboratorium akan melihat menu "Keuangan" dan "Kualitas" juga di picker Workspace-nya, bukan cuma "LIMS"). Ini kemungkinan besar konsisten dengan keputusan supervisor 2026-07-24 ("tampilkan semua modul, jangan disembunyikan") — tapi karena itu soal Block Modules per-user, bukan soal role-restriction di Workspace, **PERLU KONFIRMASI TIM**: apakah menu domain memang harus terlihat semua role, atau harusnya dibatasi juga.

**A-3 (Low).** Reports (5 di `starlab_lab_ops`, 3 di `starlab_customizations`, 1 di `starlab_quality`) **tidak ada satupun yang dipasang sebagai shortcut di Workspace manapun** — semua workspace role punya `shortcuts` array isinya cuma DocType, tidak ada tipe "Report". User harus tahu nama laporan dan cari manual lewat Report List / global search untuk menemukannya. Digabung dengan H-1 (report tidak accessible ke role terkait), ini bikin fitur laporan nyaris tidak terlihat sama sekali dari alur navigasi normal.

**A-4 (Baik/Sudah benar).** Modul ERPNext bawaan yang tidak relevan untuk bisnis lab testing (Manufacturing, Quality Management bawaan, Stock) sudah di-`is_hidden` lewat patch `restructure_desk_modules.py`, terverifikasi **sudah berjalan** di instance live saat ini (`is_hidden: 1` terkonfirmasi + tercatat di Patch Log). Workspace "Assets" sudah dipindah nesting ke bawah "Keuangan" sesuai maksud dokumen keputusan fitur. Ini bagian yang sudah rapi, tidak perlu disentuh.

### 4.B — RBAC

Lihat Bagian 2 (matriks) untuk data mentah. Ringkasan temuan RBAC tersendiri (di luar yang sudah dibahas per-role di Bagian 3):

**B-1 = C-2 (Critical).** Direksi tidak punya akses sama sekali ke Bank Account/Bank Transaction/Bank Reconciliation Tool/Bank Statement Import, bertentangan langsung dengan `docs/keputusan_bisnis_terbaru.md` poin 9 ("hanya Finance dan Direksi yang boleh akses"). **Lokasi fix:** `starlab_customizations/starlab_customizations/fixtures/custom_docperm.json` — tambah baris Custom DocPerm role Direksi (read-only kemungkinan cukup, sesuai keputusan cuma soal "akses", bukan "kelola") untuk keempat DocType tsb, lalu re-sync fixtures (`bench migrate` / `bench --site starlab.local migrate`).

**B-2 = C-4 (Critical, perlu verifikasi manual).** DocPerm base memberi `submit: 1` mentah ke Administrasi di Quotation (dan implisit ke role manapun yang jadi actor tahap Workflow terakhir di doctype lain). Saya membaca source `frappe/model/workflow.py` (`validate_workflow()`, baris 243-291) dan mengonfirmasi bahwa Frappe **hanya** memblokir perubahan **field workflow_state** yang tidak sah untuk role tsb — ia **tidak** memblokir aksi `doc.submit()` mentah selama field workflow_state tidak ikut diubah dalam call itu. Karena DocPerm dasar Quotation sudah mengizinkan Administrasi `submit`, secara teori seorang Administrasi bisa memanggil submit langsung (lewat REST API `/api/resource/Quotation/<name>` dengan `docstatus=1`, atau lewat `bench console`/skrip lain) pada Quotation yang masih Draft, **melewati seluruh rantai approval MT→MM→Direksi**, karena satu-satunya pemeriksaan yang tersisa adalah DocPerm dasar yang memang sudah "iya".
  Saya mencoba mereproduksi ini langsung di instance (lihat Lampiran), tapi terhambat bug lain yang tidak berhubungan (lihat H-5) sebelum sempat sampai ke langkah submit — jadi belum 100% terverifikasi end-to-end secara langsung, tapi jalur kode sumbernya sudah saya baca sendiri dan cukup meyakinkan untuk ditandai Critical + **wajib jadi test case eksplisit besok** (coba submit Quotation Draft sebagai Administrasi lewat API, bukan lewat tombol UI Workflow).
  **Fix kalau terkonfirmasi nyata:** turunkan `submit: 0` di baris Custom DocPerm Administrasi/Quotation (baris 2-27, `fixtures/custom_docperm.json`) — biarkan `submit` cuma dipegang Direksi (yang memang sudah punya), karena aksi submit final semestinya hanya lewat transisi Workflow "Setujui" di state terakhir.

**B-3 = H-2 (High).** `delete: 1` diberikan pada dokumen yang **sudah melewati approval** dan **bukan submittable** (tidak ada proteksi docstatus bawaan Frappe):
  - Administrasi → Petty Cash Entry (termasuk yang statusnya "Disetujui" dan sudah punya Journal Entry terkait — hapus record ini akan meninggalkan Journal Entry "yatim" tanpa entry asalnya)
  - Laboratorium → Test Result (termasuk yang sudah "Divalidasi")
  - Manajer Mutu → Document Master (termasuk yang sudah "Aktif" — pelanggaran retensi rekaman ISO 17025)
  **Rekomendasi:** pertimbangkan `delete: 0` untuk role-role ini pada DocType tsb (biarkan cuma create+write di state awal; kalau butuh "batalkan" pakai transisi Workflow ke state terminal, bukan hard delete), atau minimal batasi lewat `if_owner` + kondisi state di level UI/hook kalau delete memang harus tetap ada untuk skenario "salah input, buru-buru hapus sebelum diajukan".

**B-4 = H-3 (High).** `notify_role_via_whatsapp` (`starlab_integrations/starlab_integrations/whatsapp.py`) adalah `@frappe.whitelist()` (tanpa `allow_guest`) tapi **tanpa pengecekan permission tambahan apapun di dalam body function** — user manapun yang sudah login (role serendah apapun) bisa memanggil endpoint ini dengan parameter `role` dan `message` bebas, memicu pengiriman WhatsApp (lewat API berbayar Fonnte/Twilio/dst.) ke seluruh user pemegang role yang diminta, dengan isi pesan bebas pula. **Rekomendasi:** tambah pengecekan role pemanggil (mis. hanya System Manager/Direksi/Manajer Mutu yang boleh trigger broadcast manual), atau minimal `frappe.only_for("System Manager")` di awal function.

**B-5 (Medium, M-3).** Semua 7 role punya `write+create` di Document Master, dengan Workflow yang mengizinkan tiap role mengajukan dokumen atas nama divisinya sendiri (`doc.owner_division == '<kode divisi>'`). Ini **sesuai desain** `document_control_hooks.py` (row-level permission berdasarkan divisi, bukan bug), tapi berarti setiap divisi bisa membuat/mengedit dokumen mutu mereka sendiri sebelum diajukan — **PERLU KONFIRMASI TIM**: apakah ini memang model yang diinginkan (self-service document authoring per divisi), atau semestinya hanya Manajer Mutu yang boleh create Document Master apapun dan divisi lain cuma mengajukan draft/request.

**B-6 (Medium, M-5).** Struktur self-approval: pada Document Master, Manajer Mutu bisa `Ajukan` dokumen miliknya sendiri (kalau `owner_division == 'MM'`) **dan** juga satu-satunya role yang bisa `Setujui` di tahap "Menunggu Approval MM" — jadi dokumen milik divisi MM sendiri, tahap approval pertamanya efektif "disetujui sendiri" sebelum lanjut ke Direksi. Semua transisi di seluruh sistem (Quotation, Document Master, Work Order, Sample, Test Result, Petty Cash, Client Inquiry) memakai `allow_self_approval: 1` tanpa pengecualian — cek apakah ini memang keputusan sadar (karena rantai approval tetap berlanjut ke role lain di tahap berikutnya untuk sebagian besar kasus) atau perlu di-review khusus untuk kasus MM di atas.

**B-7 (Baik/tervalidasi positif).** Pemisahan peran pembuat vs validator di Test Result **sudah benar secara struktural**: Laboratorium (create+ajukan validasi) ≠ Manajer Teknis (validasi/tolak) — role berbeda meski `allow_self_approval:1` tetap ada di flag Workflow-nya (ini flag generik Frappe, bukan berarti orangnya sama). Baik juga: `has_permission`/`get_permission_query_conditions` untuk Document Master (`starlab_quality/starlab_quality/document_control_hooks.py`) **fail-closed** untuk role yang tidak dipetakan (mis. Customer) — dikonfirmasi lewat pembacaan kode langsung, bukan asumsi.

### 4.C — Tampilan (UI/UX)

**C-UX-1 (Low, L-1).** Print Format klien-facing "Quotation Ringkasan Harga" menampilkan catatan internal ke PDF yang dikirim ke klien: *"Catatan: posisi Rush Fee di urutan kalkulasi ini ... masih ASUMSI kerja PRD v8 Sprint 12 -- belum dikonfirmasi eksplisit ke PO."* Ini dua masalah sekaligus: (1) teks debug/internal seharusnya tidak pernah muncul di dokumen resmi yang dikirim ke klien, dan (2) sejak 2026-07-30 pertanyaan ini **sudah dijawab** (lihat C-1 di bawah) jadi kalimatnya juga sudah basi/salah. **Fix:** hapus paragraf catatan ini dari `print_format/quotation_ringkasan_harga/quotation_ringkasan_harga.json` begitu C-1 selesai di-fix.

**C-UX-2 (Informational).** Tidak ditemukan field `hidden` yang janggal atau field penting yang tersembunyi di seluruh DocType custom — cukup bersih, tidak ada clutter field yang jelas-jelas tidak perlu.

**C-UX-3 (Informational).** Tidak bisa saya verifikasi secara visual (responsiveness, layout form rusak di ukuran layar tertentu, dll.) karena saya tidak punya akses browser di sesi ini — **ini murni harus dicek manual oleh tim besok**, bukan sesuatu yang bisa saya konfirmasi lewat pembacaan kode/API.

**C-UX-4 (Baik).** Dashboard per role (7 Dashboard dengan Number Card + 1 Chart masing-masing) cukup relevan/informatif untuk role terkait — Finance melihat Invoice Overdue/Unpaid/Due, Laboratorium melihat Sample Belum Diuji/Sedang Diuji, dst. Tidak ada dashboard yang isinya generik/tidak nyambung dengan role pemiliknya.

### 4.D — Efisiensi Sistem

**D-1 (Medium, M-2).** Beberapa auto-transition status (`wo_hooks.py` di `starlab_lab_ops`, `quotation_hooks.on_update` di `starlab_customizations`, `lhu_hooks.py`) sengaja memakai `doc.db_set()`/`frappe.db.set_value()` untuk mem-bypass Workflow engine — developer sendiri menulis komentar eksplisit bahwa ini juga berarti perubahan itu **tidak tercatat di Version/Track Changes log** dokumen (cuma lewat Comment manual di sebagian kasus). Untuk laboratorium terakreditasi ISO 17025 yang butuh jejak audit lengkap, ini technical debt yang perlu diketahui — bukan blocker testing fungsional besok, tapi harus di-catat sebagai risiko sebelum go-live produksi sungguhan.

**D-2 (Low).** N+1 query pattern (satu query per baris di dalam loop) ditemukan di beberapa scheduled task dan hook: `tasks.py` (`_notify_role` dipanggil di dalam loop expiry/overdue), `lhu_hooks.py::populate_test_result_list`, `starlab_lab_ops/tasks.py` (3 fungsi reminder). Untuk volume data kecil (situasi testing besok, database dev/demo) ini tidak akan terasa — flag ini murni untuk kesiapan skala produksi nanti, bukan untuk besok.

**D-3 (Low).** 8 dari 9 custom report (semua di `starlab_lab_ops`, plus `Laporan Keuangan Operasional`) memakai raw SQL **tanpa LIMIT/pagination**. Sama seperti D-2, tidak masalah untuk data testing kecil, tapi technical debt untuk data produksi nanti.

**D-4 (Low, L-3).** 5 Role Profile bawaan ERPNext (Purchase/Sales/Accounts/Manufacturing/Inventory) dan puluhan Role bawaan yang tidak relevan (Manufacturing Manager, Purchase Master Manager, dll.) masih ada di sistem meski tidak dipakai — bukan bug fungsional, tapi berpotensi bikin admin baru salah pilih Role Profile/Role kalau menambah user manual di masa depan. Pertimbangkan didokumentasikan mana yang "resmi dipakai" vs "warisan ERPNext, abaikan".

**D-5 (High, H-4 — soal proses, bukan kode).** Dua patch (`restructure_desk_modules.py`, `restructure_selling_and_org_menu.py`) **baru saja diperbaiki** (uncommitted per `git status` saat audit ini berjalan) dari bug yang sebelumnya bikin `ModuleNotFoundError`/`AttributeError` saat `bench migrate` — versi lama mengacu ke DocType (`Workspace Customization`) dan field (`Workspace.sidebar_items`) yang **tidak ada** di versi Frappe yang benar-benar ter-install di project ini (`version-16`). Saya verifikasi versi yang diperbaiki **sudah berhasil jalan** di container live saat ini (`is_hidden=1` terkonfirmasi + tercatat di Patch Log DB). **Tapi perubahan ini belum di-commit ke git.** Kalau container di-rebuild ulang dari image/commit terakhir sebelum testing besok (restart `docker compose`, clone fresh ke laptop lain untuk demo, dst.), fix ini akan **hilang** dan migrate akan gagal lagi seperti sebelumnya. Ini bukan temuan kode, tapi git-hygiene, namun konsekuensinya bisa langsung menghambat testing besok kalau ada yang perlu setup ulang instance di menit-menit terakhir. **Rekomendasi:** commit ketiga file yang termodifikasi (`restructure_desk_modules.py`, `restructure_selling_and_org_menu.py`, `seed_test_users.py`) sesegera mungkin — sesuai kebijakan repo ini, saya tidak melakukan commit apapun sendiri, jadi ini murni catatan untuk tim.

---

## Bagian 5 — Temuan yang Terhubung Langsung ke Keputusan Bisnis Tertulis

Dua temuan berikut **bukan** soal "belum tahu maunya apa" — jawabannya sudah ada tertulis di `docs/keputusan_bisnis_terbaru.md` (dikumpulkan 2026-07-30), tapi kodenya belum disesuaikan. Ini yang paling penting untuk diketahui tim sebelum testing besok, karena kalau testing jalan begini apa adanya, hasilnya akan menguji formula/RBAC yang **stakeholder sendiri sudah bilang salah**.

**C-1 (Critical) — Rush Fee masih ikut kena Discount.**
Keputusan (poin 1, prioritas "tinggi" menurut dokumen itu sendiri): *"Diskon cuma boleh kena ke bagian pengujian, Rush Fee TIDAK boleh ikut kediskon."* Tapi kode saat ini (`starlab_customizations/starlab_customizations/quotation_hooks.py`, fungsi `_calculate_price_summary`) masih menghitung Discount dari basis `sub_total + rush_fee_amount` (`base_after_rush_fee`), bukan dari `sub_total` saja. Dampaknya: setiap Quotation yang memakai Rush Fee + Discount sekaligus akan menghasilkan **Total Invoice yang lebih kecil dari seharusnya** (karena Rush Fee ikut terpotong diskon, padahal seharusnya tidak). Ini uang, dan langsung terlihat oleh klien di print PDF. **Lokasi fix:** `quotation_hooks.py::_calculate_price_summary` (lokasi sudah ditandai komentar oleh developer sebelumnya) — dan jangan lupa hapus catatan caveat terkait di print format (lihat C-UX-1).

**C-2 (Critical) — sudah dibahas di B-1 di atas** (akses Bank Account/Transaction untuk Direksi).

---

## Bagian 6 — Kesimpulan Kesiapan Testing (Go / No-Go)

**GO — dengan syarat.** Fondasi sistem (DocType, Workflow, sebagian besar RBAC) sudah cukup matang untuk sesi testing dimulai besok; ini bukan sistem yang "belum jadi". Tapi ada 3 hal yang sebaiknya diselesaikan atau minimal dikomunikasikan eksplisit ke seluruh tim tester **pagi ini/sebelum sesi mulai**, supaya testing besok menghasilkan sinyal yang valid, bukan false positive/false negative:

1. **Wajib:** pastikan seluruh tester memakai akun `*.test@example.com` (bukan `test.*@starlab.local`) untuk role-play — kalau tidak, semua temuan RBAC dari sesi testing besok tidak bisa dipercaya (lihat 1.2).
2. **Sangat disarankan sebelum mulai:** cek cepat apakah `/status-klien` (Client Portal) benar-benar berfungsi untuk user Customer — kalau ternyata error permission seperti dugaan saya (C-5), ini blocker besar untuk skenario client-facing dan lebih baik ketahuan di menit pertama daripada di tengah sesi.
3. **Sangat disarankan sebelum mulai:** commit 3 file yang saat ini uncommitted (D-5) supaya environment tidak berisiko rusak kalau ada yang perlu restart/rebuild container di tengah hari.

Item C-1 (Rush Fee) dan C-2 (akses Bank Direksi) **tidak harus** menghalangi mulainya testing (testing tetap bisa jalan untuk skenario lain), tapi kalau skenario uji besok mencakup Quotation dengan Rush Fee+Discount atau akses data perbankan oleh Direksi, hasilnya **sudah pasti gagal** sampai kode diperbaiki — lebih baik tim tahu ini dari awal daripada menemukan "bug" yang sebenarnya sudah diketahui.

Sisanya (High/Medium/Low) tidak menghalangi testing sama sekali — bisa masuk backlog perbaikan pasca-testing.
