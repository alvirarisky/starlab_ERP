# Audit Project ERP SAI — Sebelum Sprint 5

**Tanggal audit:** 2026-07-26
**Lingkup:** Audit teknis menyeluruh (read-only, tidak ada perubahan kode) terhadap implementasi Frappe/ERPNext untuk PT Starlab Analitik Indonesia (SAI), sebelum melanjutkan pekerjaan ke Sprint 5.
**Sumber pembanding:** BRA ERP SAI, TSD ERP SAI v2.0, PRD Quotation & Master Data v6.

---

## 0. Catatan Penting Soal Environment

Ada **dua lokasi berbeda** yang perlu dibedakan dengan tegas:

1. **`/workspace/development`** — workspace yang sedang dibuka di editor. Ini sebenarnya adalah **scaffold `frappe_docker`** (riwayat git-nya berisi commit soal proxy/CI/docker, tidak ada hubungannya dengan bisnis SAI). Folder `frappe-bench/apps/starlab_*` di dalamnya adalah hasil **extract manual** dan sengaja tidak punya riwayat git sendiri.
2. **`~/starlab-erp-project`** — repo git **asli** proyek SAI, terhubung ke GitHub (`origin`, branch `develop`). Di sinilah seluruh riwayat commit pengembangan Sprint 1–4 benar-benar tercatat.

Audit ini menggabungkan: (a) pembacaan kode aktual dari `frappe-bench/apps/*` di `/workspace/development`, dan (b) analisis `git log` dari `~/starlab-erp-project`.

---

## 1. Struktur Repository & Bench

```
/workspace/development/
├── apps-example.json          (contoh: erpnext branch version-16)
├── installer.py
└── frappe-bench/
    ├── apps/
    │   ├── frappe/                     (core framework)
    │   ├── erpnext/                    (core ERPNext)
    │   ├── starlab_customizations/     ✅ ada
    │   ├── starlab_lab_ops/            ✅ ada
    │   └── starlab_quality/            ✅ ada
    │       ⚠ starlab_integrations TIDAK ADA sama sekali (belum di-scaffold)
    └── sites/starlab-erp.localhost/
        └── site_config.json → installed_apps:
            ["frappe","erpnext","starlab_lab_ops","starlab_customizations","starlab_quality"]
```

`common_site_config.json` dan `sites/apps.txt` mengonfirmasi hal yang sama: site hanya berisi 3 dari 4 custom app yang direncanakan TSD. **`starlab_integrations`** (WhatsApp Gateway + REST API Client Dashboard) **belum pernah dibuat** — tidak ada direktori, tidak ada di `apps.txt`, tidak ter-install. Ini **sesuai ekspektasi** (memang scope Sprint 10 TSD), jadi bukan gap, hanya konfirmasi.

Setiap app custom mengikuti struktur bench standar (`starlab_x/starlab_x/starlab_x/doctype/...`), masing-masing punya `hooks.py`, `modules.txt`, `fixtures/` (kecuali `starlab_quality`, lihat §8), `patches.txt` (kosong di ketiganya), `setup/` (script provisioning one-off), dan `docs/`.

---

## 2. Analisis DocType

### 2.1 `starlab_customizations`

| DocType | Field kunci | Controller (.py) | Client Script (.js) |
|---|---|---|---|
| **Petty Cash Entry** | `tanggal`, `item`, `nominal` (Currency, reqd), `bukti` (Attach Image, reqd), `keterangan`, `status` (Draft/Menunggu Approval/Disetujui/Ditolak), `journal_entry` (Link, read-only), `disetujui_oleh` | `class PettyCashEntry(Document): pass` — **stub kosong, tanpa validasi apa pun** | boilerplate ter-comment penuh |
| **Quotation Parameter Detail** (child) | `parameter` (Link→Test Parameter, reqd), `matriks`/`regulasi_acuan` (fetch_from), `frekuensi` (Int, default 1), `qty_per_titik` (Int, default 1), `harga_satuan` (fetch_from Test Parameter), `harga_total` (Currency, read-only) | stub kosong | n/a |

### 2.2 `starlab_lab_ops`

| DocType | Field kunci | Controller | JS |
|---|---|---|---|
| **Test Parameter** | `parameter_name` (unique), `matriks` (8 pilihan), `regulasi_acuan`, `satuan`, `harga_satuan_default`, `status`, `metode_uji` (Link→**Document Master**, ditambahkan belakangan via migration terpisah — lihat §7) | stub kosong | comment stub |
| **Work Order Pengujian** | `naming_series` (`P.SAI.####.MM.YYYY`), `customer`, `quotation` (opsional), `kegiatan`, `tanggal_wo`, `status` (Draft/Approved/In Progress/Completed/Cancelled), `penerimaan_sampel`, `wo_parameter_detail` (child); custom field `alasan_buka_kembali` ditambahkan belakangan | stub kosong | comment stub |
| **WO Parameter Detail** (child) | `matriks`, `parameter`, `sample_id_range`, `pj_analis`, `target_pengujian`, `status_pengujian` (Pending/In Progress/Done/Subkon), `keterangan` | stub kosong | n/a |
| **Sample** | `sample_id` (unique), `work_order`, `matriks`, `tanggal_terima`, `status` (Diterima/Sedang Diuji/Divalidasi/Diarsipkan/Dimusnahkan), `retensi` (Tahan/Bisa Dibuang), `tanggal_musnah`, `catatan_kondisi` | stub kosong | comment stub |
| **Test Result** *(di luar scope Sprint 1–4)* | `sample`, `work_order` (fetch), `parameter`, `analis`, `hasil_uji`, `satuan` (fetch), `qc_detail` (child), `status` (Draft/Diajukan Validasi/Divalidasi/Ditolak), `validated_by`, `validated_on`, `locked`, `catatan_validasi` | stub kosong | comment stub |
| **QC Detail** (child) *(di luar scope)* | `qc_type` (Kurva Kalibrasi/Ripitabilitas/Trueness), `nilai_slope`, `nilai_intersep`, `nilai_r2`, `nilai_rpd_persen`, `nilai_trueness_persen`, `keterangan` | stub kosong | n/a |
| **LHU** *(di luar scope)* | `naming_series` (`LHU-####-MM-YYYY`), `work_order`, `customer` (fetch), `tanggal_terbit`, `diterbitkan_oleh`, `test_result_list` (child), `status` (Draft/Issued/Revised/Superseded), `file_lhu` | stub kosong | comment stub |
| **LHU Test Result Detail** (child) *(di luar scope)* | `test_result`, `parameter`/`hasil_uji`/`satuan` (fetch), `metode_acuan` (**tidak ada fetch_from** — lihat §12 Bug Potensial) | stub kosong | n/a |

### 2.3 `starlab_quality` *(seluruh modul ini di luar scope Sprint 1–4, tapi sudah ada penuh)*

| DocType | Field kunci | Controller | JS |
|---|---|---|---|
| **Document Master** | `document_no` (unique), `document_name`, `document_level` (PM/PO/IKM/DP), `edisi_revisi`, `tanggal_efektif`, `owner_division`, `status` (Aktif/Dalam Revisi/Usang), `file_dokumen`, `distribusi` (child), `revisi_history` (child, read-only) | `class DocumentMaster(Document): pass` — stub kosong | comment stub |
| **Document Distribution** (child) | `divisi`, `tanggal_distribusi`, `acknowledged`, `acknowledged_on` | stub | n/a |
| **Document Revision** (child) | `revisi_ke`, `tanggal_revisi`, `diubah_oleh`, `ringkasan_perubahan`, `file_versi_lama` | stub | n/a |

**Catatan konsisten di seluruh 3 app**: *semua* controller `.py` custom DocType adalah stub `pass` kosong tanpa logika apa pun, dan *semua* client script `.js` adalah boilerplate yang di-comment total (`frappe.ui.form.on(...) { refresh(frm) {} }`). Tidak ada satu pun logic client-side di seluruh project. Seluruh logika bisnis nyata berada di file hook terpisah (`quotation_hooks.py`, `wo_hooks.py`) — lihat §5.

---

## 3. Analisis Workflow

| Workflow | App | State | Transition penting |
|---|---|---|---|
| **Quotation** | `starlab_customizations` | Draft → Menunggu Approval MT → MM → **Finance** → Marketing → Direksi → Approved / Rejected / Cancelled (9 state) | Actions: Ajukan/Setujui/Tolak/Revisi/Batalkan. **Cocok dengan PRD v6 §5.4** (rantai MT→MM→Finance→Marketing→Direksi), termasuk keberadaan Finance yang sempat dipertanyakan di PRD tapi dikonfirmasi. |
| **Work Order Pengujian** | `starlab_lab_ops` | Draft → Approved → In Progress → Completed → Cancelled (5 state) | `Setujui` (MT), `Mulai Pengujian` (Lab), `Selesaikan` (MT, tapi *sebenarnya di-otomatisasi via `db_set` — lihat §12*), `Batalkan` (Direksi/MT), `Buka Kembali` (MT, wajib isi alasan) |
| **Sample** | `starlab_lab_ops` | Diterima → Sedang Diuji → Divalidasi → Diarsipkan → Dimusnahkan (5 state) | `Mulai Uji`, `Arsipkan`, `Musnahkan` (kondisi retensi dievaluasi di Python, bukan di expression Workflow Transition — workaround bug sandbox) |
| **Document Control** (TSD §6.6) | `starlab_quality` | **TIDAK ADA** | DocType Document Master sudah ada lengkap dengan field `status`, tapi **tidak ada Frappe Workflow yang mengikat transisi status-nya** — approval MM→Direksi→Aktif yang didefinisikan TSD Bab 6.6 belum diimplementasikan sebagai workflow engine, hanya field Select biasa. |
| Client Inquiry, Kaji Ulang, T&C, Test Result, LHU, Invoice, Petty Cash | — | **Tidak ada** | Sesuai ekspektasi untuk Client Inquiry/Kaji Ulang/T&C (memang scope Sprint 5); **tapi Test Result, LHU, dan Petty Cash sudah punya DocType-nya, hanya belum punya Workflow** — beda dengan rencana TSD §6.5/6.8 yang mengasumsikan semua itu pakai Frappe Workflow. |

---

## 4. Analisis Report

| Report | App | Tipe | Ref. DocType | Status vs scope |
|---|---|---|---|---|
| Laporan Keuangan Operasional | `starlab_customizations` | Script Report | Petty Cash Entry | Di luar Sprint 1–4 (menggabungkan Petty Cash + Journal Entry) |
| Laporan Kinerja SLA Pengujian | `starlab_lab_ops` | Script Report + bar chart | Work Order Pengujian | Di luar Sprint 1–4 |
| Rekap Hasil Uji per Parameter | `starlab_lab_ops` | Script Report + bar chart | Test Result | Di luar Sprint 1–4, bergantung pada Test Result (data model Sprint 6) |
| Rekap Work Order | `starlab_lab_ops` | Script Report | Work Order Pengujian | Sesuai scope (Sprint 3) |
| Status Sample Realtime | `starlab_lab_ops` | Query Report (raw SQL) | Sample | Sesuai scope (Sprint 4) |
| Rekap Stok Reagen dan Consumable | `starlab_lab_ops` | Query Report (raw SQL, join `tabItem`/`tabItem Reorder`/`tabBin`) | Item | ⚠️ Di luar Sprint 1–4 **dan** menyentuh domain Inventory yang PRD v6 secara eksplisit tandai **Out of Scope** ("direkomendasikan jadi PRD terpisah") |
| Rekap Kepatuhan Dokumen Mutu | `starlab_quality` | Query Report (raw SQL) | Document Master | Di luar Sprint 1–4 |

Print Format: **LHU Resmi** (`starlab_lab_ops`) — Jinja print format untuk LHU. HTML-nya berisi disclaimer eksplisit dari developer: *"Kop surat, logo, dan alamat pada dokumen ini masih berupa placeholder Fase 2 dan akan dilengkapi pada sprint resmi."*

---

## 5. Analisis API (Whitelisted Methods)

**Nihil.** Grep `frappe.whitelist` di seluruh 3 app (`starlab_customizations`, `starlab_lab_ops`, `starlab_quality`) menghasilkan **0 hit**. Tidak ada satu pun REST endpoint custom. Ini konsisten dengan `starlab_integrations` (rumah rencana seluruh API — WhatsApp gateway, Client Dashboard REST endpoint) yang memang belum dibuat.

---

## 6. Analisis Permission

| DocType | Custom DocPerm (fixture) | Catatan |
|---|---|---|
| Quotation | 13 entri (`starlab_customizations`) | Administrasi: create/write/submit; Direksi: cancel/submit/write; MT/MM/Finance/Marketing: read+write, tanpa submit |
| Customer | termasuk dalam 13 entri di atas | Read-only untuk MT/MM/Finance/Marketing/Direksi/Administrasi |
| Work Order Pengujian & Sample | 13 entri (`starlab_lab_ops`) | Peran: Manajer Teknis, Laboratorium, Direksi, Marketing, Finance, Administrasi |
| Document Master/Distribution/Revision | **Tidak ada custom permission** | Hanya permission default `System Manager` bawaan doctype.json — **tidak ada role SAI (MM, Direksi, dst.) yang di-grant akses** sama sekali ke modul Document Control, padahal modul ini sudah fungsional dan diseed data dummy |

7 Role fixture terdaftar (`starlab_customizations/fixtures/role.json`): Direksi, Manajer Teknis, Manajer Mutu, Finance, Marketing, Administrasi, Laboratorium — sesuai 7 divisi BRA/TSD.

---

## 7. Analisis Custom Script

**Nihil di seluruh project.** Tidak ditemukan Client Script atau Server Script (baik sebagai fixture maupun record DocType) di ketiga app. Seluruh `.js` client-side adalah boilerplate ter-comment. Ini berarti:
- Tidak ada validasi/UX di sisi client (semua baru ketahuan salah setelah submit ke server).
- Tidak ada auto-fetch/format tambahan di form.

---

## 8. Analisis Hooks

| App | `doc_events` aktif | `fixtures` list | Catatan |
|---|---|---|---|
| `starlab_customizations` | `Quotation.validate → quotation_hooks.validate` | Role, Workflow State, Workflow Action Master, Workflow (Quotation), Custom Field (Quotation), Custom DocPerm (Quotation, Customer) | scheduler/override hooks semua di-comment (boilerplate tidak dipakai) |
| `starlab_lab_ops` | `Work Order Pengujian.validate/on_update`, `Sample.validate`, `Test Result.on_update` → semua di `wo_hooks.py` | Workflow State, Workflow Action Master, Workflow (WO Pengujian, Sample), Custom Field (WO Pengujian), Custom DocPerm (WO Pengujian, Sample), Number Card (2) | `required_apps=["erpnext"]`; comment eksplisit: Workspace **sengaja tidak difixturekan** karena privat ke user dev/test `tester@starlab.local` |
| `starlab_quality` | **Tidak ada** (`doc_events` di-comment total) | **Tidak ada `fixtures` list sama sekali** | Document Master/Revision/Distribution **tidak reproducible** di instance baru — hanya ada karena setup script pernah dijalankan manual sekali di DB ini |

**Logic bisnis nyata (isi file hook):**
- `quotation_hooks.py`: hitung `harga_total` tiap baris parameter, set `tanggal_kadaluwarsa = transaction_date + 30 hari`.
- `wo_hooks.py`:
  - `validate_work_order`: mencegah WO dibuka kembali dari Completed→In Progress tanpa `alasan_buka_kembali` terisi.
  - `on_update_work_order`: auto-set status WO ke Completed via `doc.db_set(...)` (bypass Workflow engine) begitu semua baris parameter selesai — dengan justifikasi bahwa user Laboratorium tidak punya transisi Workflow "Selesaikan" sendiri.
  - `validate_sample`: guard transisi Musnahkan (workaround bug sandbox eval date-vs-string), plus auto-flip WO Approved→In Progress saat sample pertama diterima.
  - `on_update_test_result`: auto-promosikan Sample ke Divalidasi begitu semua Test Result tervalidasi.

---

## 9. Analisis Fixtures

| App | Fixtures diekspor |
|---|---|
| `starlab_customizations` | Role (7), Workflow State (9, filter), Workflow Action Master (5), Workflow (Quotation), Custom Field (Quotation, 9 entri — termasuk `crm_deal` yang tampak tidak relevan/nyasar dari CRM ERPNext), Custom DocPerm (13 entri) |
| `starlab_lab_ops` | Workflow State (7), Workflow Action Master (6), Workflow (WO Pengujian, Sample), Custom Field (`alasan_buka_kembali`), Custom DocPerm (13 entri), Number Card (2) |
| `starlab_quality` | **Kosong — tidak ada `fixtures/` folder sama sekali** |

Selain fixtures resmi, ditemukan **script seed data** untuk demo/testing:
- `seed_fase1_master_data.py`: 5 Customer, 7 Employee (7 designasi sesuai divisi), 5 Item reagen (dengan Reorder Level), 10 Test Parameter.
- `seed_fase2_dummy_data.py`: 5 Document Master, 10 Work Order Pengujian, 20 Sample, 30 Test Result, **5 LHU, 5 Petty Cash Entry**, dummy Journal Entry, dummy Sales Invoice, dummy Bank/Bank Account/Bank Transaction/Payment Entry, dan Stock Reconciliation "stok kritis".

Script kedua ini secara eksplisit men-seed 3 DocType yang berada di luar Sprint 1–4 (Document Master, LHU, Petty Cash Entry) di bawah label informal **"Fase 2"** — mengonfirmasi developer sebelumnya sadar sedang mengerjakan hal di luar roadmap resmi.

**Catatan hygiene**: `starlab_lab_ops` punya **dua folder `setup/`** (satu di level app top-level, satu lagi nested di `starlab_lab_ops/starlab_lab_ops/setup/`) dengan isi yang tumpang tindih tapi tidak identik — folder nested berisi lebih banyak script (report/print format creation). Tidak jelas mana yang jadi sumber kebenaran; tidak diwire ke `hooks.py` atau `patches.txt` — seluruh DocType/Report/Print Format dibuat via `bench execute` satu per satu secara manual, bukan lewat migration resmi.

---

## 10. Analisis Git (`~/starlab-erp-project`, branch `develop`)

### 10.1 Overview

- **Remote**: `origin` → `github.com/alvirarisky/starlab_ERP`, branch kerja: `develop` (19 commit).
- **Rentang waktu**: 2026-07-21 → 2026-07-26 (**6 hari kalender**).
- **Kontributor**: `Nnopir` (18 commit — developer utama/tunggal untuk seluruh fitur), `vrrry` (1 commit — commit inisialisasi pertama). Sejak commit ke-2, hampir semua pesan commit menandai `Co-Authored-By: Claude Sonnet 5` — proyek ini dibangun dengan AI-pairing sejak hari kedua.
- **Branch lain**: `main` (riwayat **tidak terhubung** — dump bench penuh 9.240 file, backup/referensi, **bukan** bagian dari riwayat fitur nyata), `app-starlab-customizations`/`app-starlab-lab-ops`/`app-starlab-quality` (hasil `git subtree split` dari `develop`, tidak ada kerja baru), `feature/buat-kelfin` (branch yatim, hanya edit README, tidak pernah di-merge). Tidak ada tag, tidak ada stash.

### 10.2 Breakdown Kronologis

| Fase | Commit | Ringkasan |
|---|---|---|
| **0. Bootstrap** (21–22 Jul) | `03fe761`, `3c27132`, `5b9aa39` | Scaffold 4 app via `bench new-app`, setup docker dev stack + CI, fix CI mariadb config |
| **1. Dokumen perencanaan** (23–24 Jul) | `ee3813c`, `0b64335`, `8c4094b`, `fb2162a` | Tambah PRD/BRA/TSD/Project Plan ke `docs/`; **`docs/Fase2_Plan.md` ditambahkan lalu dihapus di hari yang sama tanpa penjelasan** (satu-satunya commit "delete" di seluruh riwayat) |
| **2. Sprint 1** (24 Jul) | `88e637d` | **Commit terbesar**: 170 file, **+7.208/-0** baris, pesan commit hanya satu baris tanpa narasi. Membuat hampir semua DocType inti lintas 3 app sekaligus (Sample, Work Order Pengujian, Test Parameter, Test Result, LHU, QC Detail di `starlab_lab_ops`; Document Master/Revision/Distribution di `starlab_quality`; Petty Cash Entry di `starlab_customizations`) |
| **3. Sprint 2** (25–26 Jul) | `2926c31` | Quotation & Approval workflow (TSD §6.1+7.1). 11 file, +1.534/-7. Commit body eksplisit catat: *auto-numbering Quotation belum dikonfirmasi Administrasi, masih pakai naming series default ERPNext* |
| **4. Sprint 3** (26 Jul) | `a79aed3` | Work Order Pengujian workflow (TSD §6.2+7.2). 7 file, +510/-7. Commit body catat: *tabel role-permission TSD 7.2 sulit terbaca hasil extract PDF, direkonstruksi manual dan dikonfirmasi ke user* |
| **5. Sprint 4** (26 Jul, tip `develop`) | `1d0c0e2` | Sample workflow + dashboard awal (TSD §6.3+7.3). 7 file, +457/-4. Menambahkan 2 Number Card; Workspace sengaja tidak difixturekan |
| **6. Docker/packaging hardening** (25–26 Jul, interleaved) | `cef37d6`, `218a3e7`, `cabb536`, `f9da543`, `c6cf6b3`, `1ffc689`, `11a2937`, `64ada56` | Perbaikan berturut-turut agar 4 app bisa di-install independen via Docker (subtree branch), termasuk fix nesting Python package dan `docker/apps.json` |

### 10.3 File Paling Sering Berubah

Karena repo baru berumur 6 hari, mayoritas file hanya disentuh sekali. File yang berubah >1 kali (murni churn config/fixture, bukan indikasi kompleksitas):

| Jumlah | File |
|---|---|
| 5× | `docker/apps.json` |
| 3× | `starlab_lab_ops/starlab_lab_ops/hooks.py`, `README.md` |
| 2× | `wo_hooks.py`, `fixtures/workflow_state.json`, `fixtures/workflow_action_master.json`, `fixtures/workflow.json`, `fixtures/custom_docperm.json`, `starlab_customizations/hooks.py`, `docs/Fase2_Plan.md` (add lalu delete), `.gitignore`, `.github/workflows/ci.yml` |

Proxy scope yang lebih berguna — total *file-touches* per app sepanjang riwayat: `starlab_lab_ops` 112, `starlab_customizations` 44, `starlab_quality` 38, `starlab_integrations` 0 (belum ada).

### 10.4 Commit Terbesar (top 5 riil, di luar rename murni)

1. `88e637d` — 170 file, +7.208/-0 (Sprint 1, tanpa narasi commit)
2. `2926c31` — 11 file, +1.534/-7 (Sprint 2, Quotation)
3. `a79aed3` — 7 file, +510/-7 (Sprint 3, Work Order)
4. `1d0c0e2` — 7 file, +457/-4 (Sprint 4, Sample + dashboard)
5. `8c4094b` — 4 file, +391/-0 (dokumentasi per-app)

(Dua commit lain, `f9da543`/`cabb536`, tampil "besar" dari jumlah file tapi 0 insersi/delesi bersih — murni pemindahan/rename folder package.)

### 10.5 Bukti Pekerjaan Belum Selesai / Catatan Eksplisit Developer

- `fb2162a`: `docs/Fase2_Plan.md` dihapus di hari yang sama ia ditambahkan, tanpa alasan tercatat — **perlu ditanyakan ke developer sebelumnya**, kemungkinan ada rencana informal yang dibatalkan/direvisi.
- Sprint 2: auto-numbering Quotation **belum sesuai format SAI**, masih fallback ke default ERPNext.
- Sprint 3: tabel role-permission WO **direkonstruksi manual** dari narasi (bukan dari tabel TSD asli) karena masalah ekstraksi PDF.
- Sprint 4: workaround bug sandbox Frappe untuk kondisi transisi Musnahkan; Workspace dashboard sengaja **tidak** difixturekan (tidak akan muncul di instance baru).
- `starlab_integrations` — **0% dikerjakan**, masih scaffold app kosong sejak hari pertama, tidak pernah disentuh lagi.
- **Tidak ada test otomatis fungsional** — seluruh `test_*.py` adalah stub `IntegrationTestCase` bawaan bench (`pass` kosong), meski beberapa commit message mengklaim "diverifikasi end-to-end" — klaim ini **manual**, bukan hasil test yang tercatat di CI.
- Tidak ditemukan commit WIP/FIXME/revert — riwayat bersih dan linear, tapi ini juga berarti tidak ada jejak eksplisit soal keputusan yang berubah pikiran (selain kasus `Fase2_Plan.md` di atas).
- Packaging Docker baru stabil di 3 commit terakhir (`c6cf6b3`, `1ffc689`, `11a2937`) — deployability lewat Docker image mandiri baru divalidasi di penghujung hari terakhir, belum "battle-tested".

### 10.6 Kesimpulan Progress (dari sisi Git)

Proyek ini dikerjakan sangat cepat (6 hari, praktis 1 orang) dengan pola: **satu commit besar per sprint**, diselingi perbaikan packaging Docker. Tidak ada iterasi bertahap per DocType yang tercatat di git (Sprint 1 sekaligus 170 file dalam 1 commit) — sehingga git history tidak bisa dipakai untuk melacak evolusi desain per DocType, hanya titik akhir tiap sprint. Progress "resmi" per label commit adalah Sprint 1–4 selesai; namun **secara paralel, developer sudah mengerjakan sejumlah item Sprint 5–8 (TSD) di bawah label informal "Fase 2"** yang tidak tercermin di penomoran Sprint TSD manapun — lihat §11 dan §12.A/B/C untuk detail.

---

## 11. Cross-Check Implementasi vs TSD

### ✅ Sesuai ekspektasi Sprint 1–4 (ada & sesuai)
- Test Parameter DocType — sesuai TSD §4.2 (field `metode_uji` ditambahkan belakangan lewat migration terpisah, technically benar tapi lewat jalur tidak standar)
- Quotation Approval Workflow (Draft→MT→MM→Finance→Marketing→Direksi→Approved/Rejected/Cancelled) — sesuai PRD v6 §5.4 persis, termasuk keberadaan Finance yang PRD-nya sendiri sempat ragu lalu konfirmasi ulang
- Work Order Pengujian DocType + Workflow 5-state — sesuai TSD §4.7 & §6.3
- Sample DocType + Workflow 5-state — sesuai TSD §4.8 & §6.4
- Customer/Employee/Item — dipakai native tanpa modifikasi berlebihan, sesuai prinsip "konfigurasi native dulu"

### ✅ Sesuai ekspektasi (memang belum ada, dan benar belum ada)
- Client Inquiry (Form A) — belum ada
- Kaji Ulang Permintaan/Tender — belum ada
- T&C Master Template — belum ada
- App `starlab_integrations` — belum ada sama sekali

### ⚠️ Penyimpangan / scope creep (ada, padahal seharusnya Sprint 5+)
1. **Test Result + QC Detail** — implementasi penuh (TSD §4.9, seharusnya Sprint 6)
2. **LHU + LHU Test Result Detail + Print Format** — implementasi penuh, kop surat masih placeholder eksplisit (TSD §4.10, seharusnya Sprint 6)
3. **Petty Cash Entry + Laporan Keuangan Operasional** — implementasi penuh (TSD §4.12, seharusnya Sprint 7)
4. **Document Control (Document Master/Revision/Distribution) + Rekap Kepatuhan** — implementasi penuh tapi **tanpa Workflow dan tanpa Custom Permission** (TSD §4.11 & §6.6, seharusnya Sprint 8)
5. **5 Report tambahan** di `starlab_lab_ops` melebihi deliverable resmi Sprint 4 ("2 Number Card"); satu di antaranya (Rekap Stok Reagen) menyentuh domain Inventory yang PRD v6 tandai eksplisit **Out of Scope**
6. **Quotation**: field tambahan (`ppn_percent`, `dp_percent`, `termin_pembayaran`, `tanggal_kadaluwarsa` otomatis, `catatan_penolakan`, child table + kalkulasi `harga_total`) sudah lebih maju dari deliverable minimal Sprint 2 — tapi **belum lengkap** dibanding PRD v6 §5.3/§4.6 (belum ada `discount_percent`, `biaya_kirim`, rush fee, referensi Client Inquiry, referensi T&C, cover/company profile, Lampiran A1, histori LHU)
7. **Auto-numbering Quotation** masih native ERPNext, belum format `Quo-SAI/[bulan romawi]/[tahun]/[no]` dari BRA/PRD

### ❌ Kekurangan struktural terhadap TSD (di luar soal "belum sempat dikerjakan")
- `starlab_quality` **tidak punya `fixtures/` sama sekali** — bertentangan dengan prinsip TSD §1.3 bahwa keempat custom app harus reproducible/version-controlled dengan benar
- Seluruh DocType custom dibuat via script `setup/*.py` imperatif (`bench execute`), **bukan** lewat `patches.txt` — bertentangan dengan asumsi TSD bahwa app "dapat di-deploy terpisah bila diperlukan" (§1.3) melalui mekanisme standar Frappe

---

## 12. LAPORAN A–H

### A. Fitur yang Sudah Selesai

1. Master Data dasar (Customer/Employee/Item) — native ERPNext, tanpa modifikasi berlebihan, sesuai rencana minimal Sprint 1.
2. **Test Parameter** — DocType lengkap sesuai TSD.
3. **Quotation Approval Workflow** — 9 state, rantai MT→MM→Finance→Marketing→Direksi, sesuai PRD v6 §5.4, diklaim developer "diverifikasi end-to-end".
4. **Quotation** — sebagian field terstruktur (PPN%, DP%, termin, expiry otomatis, catatan penolakan, child table parameter dengan kalkulasi harga otomatis).
5. **Work Order Pengujian** — DocType + Workflow 5-state + logika auto-transition status.
6. **Sample** — DocType + Workflow 5-state + logika auto-transition + guard retensi/pemusnahan.
7. **Dashboard awal Sample** — 2 Number Card ("Sample Belum Diuji", "Sample Sedang Diuji").
8. *(Di luar roadmap Sprint 1–4, tapi fungsional)*: **Test Result + QC Detail**, **LHU + Print Format** (kop surat placeholder), **Petty Cash Entry + laporan keuangannya**, **Document Control (ISO 17025)** penuh (DocType + report kepatuhan).
9. Script seed data demo/testing (`seed_fase1_master_data.py`, `seed_fase2_dummy_data.py`).

### B. Fitur yang Sebagian Selesai

1. **Quotation** — field inti PRD v6 belum lengkap: `discount_percent`, `biaya_kirim`, rush fee, referensi Client Inquiry, referensi T&C Master Template, cover/company profile, Lampiran A1, histori LHU klien — semua belum ada.
2. **Customer** — perluasan field `jenis_industri`, `pic_name`, `kategori_pelanggan` (TSD §4.1) **belum ada sama sekali**, padahal ini prasyarat langsung modul Quotation/Client Inquiry di Sprint 5.
3. **Dashboard/Workspace Sample** — baru 2 Number Card; Workspace-nya sendiri sengaja tidak difixturekan sehingga tidak portable ke instance baru.
4. **LHU Print Format** — struktur ada, tapi kop surat/logo masih placeholder eksplisit "Fase 2".
5. **Document Control** — DocType-nya lengkap, tapi **tanpa Workflow** (approval MM→Direksi belum jalan) dan **tanpa Custom Permission** — secara fungsional baru CRUD polos.
6. **Reproducibility/provisioning** — DocType dibuat lewat script one-off, bukan patch resmi; belum tentu bisa fresh-install murni lewat `bench migrate`.

### C. Fitur yang Belum Ada

- Client Inquiry (Form A) & seluruh alur pra-quotation.
- Kaji Ulang Permintaan/Tender.
- T&C Master Template.
- App `starlab_integrations` secara keseluruhan (WhatsApp Gateway, REST API Client Dashboard).
- Client Dashboard (baik sisi Frappe REST maupun sisi WordPress).
- Cover/Company Profile attach & Lampiran A1 pada Quotation.
- Scheduled Job untuk eskalasi SLA approval (1×24 jam) dan notifikasi auto-expiry — field `tanggal_kadaluwarsa` sudah dihitung, tapi **tidak ada automation/notifikasi berjalan** (semua `scheduler_events` di hooks yang diperiksa dalam keadaan kosong/di-comment).
- Test/unit test otomatis yang bermakna (semua stub kosong).
- Whitelisted REST API endpoint — nihil di seluruh project.
- Client Script/Server Script/UX logic apa pun — nihil.
- Workflow untuk Document Control, Test Result, LHU, Petty Cash Entry, Invoice (DocType-nya ada, workflow-nya tidak — TSD §6.5/6.6/6.7/6.8 belum diimplementasikan).
- Role Permission granular untuk Document Master/Revision/Distribution.

### D. Sprint yang Benar-Benar Selesai

Tidak ada satu Sprint pun yang **100% selesai penuh** sesuai definisi lengkap TSD/PRD — semuanya "selesai" untuk inti fungsional minimal, tapi menyisakan detail:

| Sprint | Status |
|---|---|
| **Sprint 1** (Setup & Master Data) | Selesai dari sisi keberadaan artefak data model (1 commit besar, 170 file), tapi **tanpa granularitas/tanpa test** — kualitas belum terverifikasi otomatis. |
| **Sprint 2** (Quotation & Approval) | Selesai secara fungsional inti (workflow jalan), **tapi belum menutup seluruh field PRD v6** (discount, biaya kirim, dst.) dan auto-numbering belum sesuai format SAI. |
| **Sprint 3** (Work Order Pengujian) | Selesai secara fungsional, **tapi tabel role-permission direkonstruksi manual** — perlu diverifikasi ulang terhadap TSD §7.2 asli. |
| **Sprint 4** (Sample Tracking + Dashboard) | Logika Sample selesai; **dashboard baru tahap awal** (2 Number Card, Workspace tidak portable) — TSD Bab 8 menuntut dashboard lengkap per 7 role, ini jauh dari itu. |

### E. Apakah Implementasi Sprint 1–4 Sudah Sesuai TSD?

**Secara struktur data & alur bisnis inti: ya, cukup sesuai.** DocType, field, dan state Workflow untuk Test Parameter, Quotation, Work Order Pengujian, dan Sample cocok dengan definisi TSD Bab 4 dan Bab 6.

**Namun ada 4 penyimpangan signifikan yang perlu perhatian sebelum melanjutkan:**
1. Auto-numbering Quotation belum sesuai format custom SAI dari BRA/PRD (masih default ERPNext) — deviasi dari desain yang direncanakan.
2. Role-permission Work Order Pengujian direkonstruksi manual dari narasi (bukan dari tabel TSD asli) karena masalah ekstraksi PDF — berisiko tidak 100% match dengan intent asli TSD §7.2.
3. `starlab_quality` tidak mengikuti prinsip reproducibility yang diasumsikan TSD §1.3 (tidak ada fixtures sama sekali).
4. Pola provisioning (script `setup/*.py` imperatif, bukan `patches.txt`) menyimpang dari mekanisme migrasi standar Frappe yang diasumsikan TSD — deployment ke instance baru via `bench migrate` murni **akan gagal** menghasilkan DocType-DocType ini kecuali admin menjalankan script setup secara manual dengan urutan yang benar.

### F. Technical Debt

1. **Pola logic tidak seragam antar app** — semua controller `.py` kosong, logic nyasar ke file hook terpisah (`quotation_hooks.py`, `wo_hooks.py`), tapi `starlab_quality` bahkan tidak punya file hook logic sama sekali. Menyulitkan maintenance jangka panjang karena tidak ada satu pola baku yang diikuti tim ke depan.
2. **Provisioning via script one-off** (`bench execute`), bukan `patches.txt`/migration resmi — tidak reproducible, berisiko drift antar environment (dev/staging/prod), dan bergantung pada urutan eksekusi manual yang tidak terdokumentasi secara formal (mis. `metode_uji` di Test Parameter harus dijalankan **setelah** Document Master ada).
3. **Duplikasi folder `setup/`** di `starlab_lab_ops` (top-level vs nested) — ambigu mana yang jadi source of truth, berisiko menjalankan script usang.
4. **`starlab_quality` tanpa fixtures** — modul ISO 17025 ini de facto tidak bisa di-deploy ulang ke instance baru tanpa menjalankan seluruh setup script manual satu per satu.
5. **Tidak ada test otomatis fungsional** — semua `test_*.py` stub kosong; klaim "diverifikasi end-to-end" di commit message adalah klaim manual, bukan bukti CI. Regresi Sprint 1–4 tidak akan terdeteksi otomatis begitu Sprint 5 mulai mengubah DocType yang sama.
6. **Semua client script di-comment total** — nihil validasi/UX di sisi client; semua validasi hanya terjadi di server setelah submit, berisiko UX buruk.
7. **LHU Print Format** masih placeholder kop surat — belum siap produksi/kirim ke klien.
8. **Custom field `crm_deal`** nyasar ke fixture Quotation — tampak seperti artefak modul CRM ERPNext yang tidak relevan untuk SAI, berpotensi membingungkan atau bermasalah jika modul CRM tidak aktif di server produksi.
9. **`metode_acuan`** di LHU Test Result Detail tidak auto-fetch (butuh Server Script 2-level fetch) — sudah ditandai TODO oleh developer sebelumnya tapi belum dikerjakan.
10. **Dashboard Workspace sengaja tidak difixturekan** — tidak akan muncul di instance produksi baru tanpa setup manual tambahan.
11. **Ketidaksinkronan penomoran Sprint vs scope nyata** — sejumlah item "Fase 2" informal (Test Result, LHU, Petty Cash, Document Control) sudah dikerjakan di luar proses sprint resmi TSD, tanpa code review terstruktur/test — risiko duplikasi kerja atau konflik desain saat Sprint 5–8 resmi mulai dikerjakan mengikuti roadmap TSD apa adanya.

### G. Bug Potensial

1. **`on_update_work_order`** meng-update status via `doc.db_set()` yang **bypass Workflow engine** — field `status` (juga jadi `workflow_state_field`) di-set langsung tanpa melalui validasi Workflow Transition/Action resmi. Berisiko state "melompat" tanpa syarat transisi yang semestinya divalidasi (mis. required field di action tertentu).
2. **Guard "Musnahkan"** di `validate_sample` dieksekusi saat `validate()` dokumen, bukan di level Workflow Transition condition — perlu diverifikasi apakah ini benar-benar mencegah transisi tidak valid, atau berpotensi race condition (aksi Workflow "berhasil" tercatat dulu sebelum validasi menolak).
3. **`metode_acuan`** di LHU Test Result Detail tanpa auto-fetch — berpotensi data kosong/tidak konsisten pada dokumen legal (LHU) yang diserahkan ke klien.
4. **Field `crm_deal`** di fixture Custom Field Quotation — bila modul CRM ERPNext tidak aktif di server target, berpotensi error saat `bench migrate` (field mengacu ke DocType yang mungkin tidak ada).
5. **Duplikasi folder `setup/`** di `starlab_lab_ops` — risiko human error menjalankan script yang salah/usang saat deployment baru, meski ada guard idempotensi (`frappe.db.exists`).
6. **`tanggal_kadaluwarsa`** dihitung ulang di `validate()` Quotation (`transaction_date + 30 hari`) tanpa guard status — berpotensi tanggal kadaluwarsa ter-update ulang meski Quotation sudah Approved, jika `transaction_date` berubah pasca-approval.
7. **Tidak ada scheduled job untuk eskalasi SLA/notifikasi expiry** — meski field-nya sudah ada, otomasi yang dijanjikan PRD ("SLA 1×24 jam") belum berjalan sama sekali; berisiko false confidence saat demo bahwa fitur ini "sudah ada" padahal hanya field pasif.
8. **Nihil test regresi** — risiko tinggi terjadi regresi diam-diam begitu Sprint 5 menambah field/logic baru ke DocType yang sama (Quotation, Work Order, Sample).

### H. Hal yang Perlu Diperhatikan Sebelum Sprint 5

1. **Putuskan status "Fase 2" informal** — Test Result, LHU, Petty Cash Entry, dan seluruh Document Control sudah ada & fungsional meski secara TSD resmi itu Sprint 6/7/8. Perlu keputusan eksplisit: dianggap "closed/delivered" (tinggal dipoles) atau direview ulang dulu (karena dibuat tanpa proses sprint/code-review/test formal)?
2. **Bereskan reproducibility `starlab_quality`** — export fixtures (Custom DocPerm minimal) sebelum menambah fitur baru di atasnya, supaya modul ISO 17025 ikut ter-deploy otomatis, bukan cuma menempel di database dev saat ini.
3. **Verifikasi ulang role-permission Work Order Pengujian** terhadap TSD §7.2 asli — developer sebelumnya eksplisit menyatakan tabel itu direkonstruksi manual karena PDF sulit dibaca.
4. **Klarifikasi format auto-numbering Quotation** ke Administrasi (Open Question PRD #5) sebelum makin banyak fitur Sprint 5 dibangun di atas asumsi numbering yang mungkin salah/sementara.
5. **`Test Parameter.metode_uji`** sudah Link ke `Document Master` — berarti `starlab_lab_ops` **sudah bergantung** pada `starlab_quality`. Perlu diperhatikan urutan instalasi/dependency app ke depan.
6. **Perluas Customer** (`jenis_industri`, `pic_name`, `kategori_pelanggan`) — ini prasyarat langsung Sprint 5 (Quotation §5.2 & Client Inquiry).
7. **17 Open Question di PRD v6 Bagian 10** (rush fee, TOP default, keamanan Client Dashboard, dll.) sebagian besar masih belum dijawab stakeholder — sebagian **wajib** diklarifikasi dulu sebelum implementasi Sprint 5 (Client Inquiry, T&C Template) supaya tidak membangun di atas asumsi salah. Lihat ringkasan status di PRD v6 akhir Bagian 10.
8. **Tambahkan minimal smoke test** untuk DocType yang sudah ada sebelum menambah kompleksitas Sprint 5, agar regresi Sprint 1–4 bisa terdeteksi otomatis.
9. **Pertimbangkan migrasi provisioning ke `patches.txt` resmi** (atau minimal dokumentasikan urutan eksekusi script `setup/*.py`) — supaya onboarding developer baru/deploy ke server baru tidak bergantung pada instruksi lisan/manual.
10. **`starlab_integrations` belum ada** — bukan blocker untuk Sprint 5 (itu scope Sprint 10 TSD), tapi perlu dicatat agar urutan roadmap ke depan tetap konsisten dan tidak keliru dianggap "sudah dikerjakan sebagian".
11. **Putuskan standar pola logic** — lanjutkan pola "controller kosong + file hook terpisah" (konsisten dengan 2 app existing) atau standardisasi ulang, termasuk mengisi kekosongan logic di `starlab_quality` (Document Control belum punya validasi/approval apa pun).

---

## Ringkasan Eksekutif

Progress Sprint 1–4 secara inti fungsional **ada dan berjalan** (DocType, field, dan Workflow untuk Quotation/Work Order/Sample cocok dengan TSD), tapi developer sebelumnya **juga sudah mengerjakan cukup banyak item Sprint 5–8** (Test Result, LHU, Petty Cash, Document Control) secara informal di bawah label "Fase 2" — tanpa test, tanpa review terstruktur, dan sebagian tanpa fixtures (khususnya `starlab_quality`). Sebelum mulai Sprint 5 sesuai urutan resmi TSD (Client Inquiry, Kaji Ulang, T&C Template, perluasan Quotation), disarankan lakukan langkah "bersih-bersih" dulu: putuskan nasib modul "Fase 2", bereskan reproducibility `starlab_quality`, klarifikasi beberapa Open Question PRD yang blocking, dan tambahkan minimal smoke test — supaya Sprint 5 dibangun di atas fondasi yang benar-benar solid, bukan sekadar "kelihatan sudah ada".
