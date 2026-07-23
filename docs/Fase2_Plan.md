# Fase 2 — Report Design (TSD Bagian 9) + DocType Stub Pendukung

**Status:** Draft rencana kerja, dibuat sebelum eksekusi Fase 2. Ditulis untuk jadi acuan
selama pengerjaan (dan histori keputusan) — bukan dokumen final/PRD.

**Prasyarat:** Fase 1 (Setup & Master Data) sudah selesai & terverifikasi — lihat ringkasan
di riwayat percakapan. Company, Fiscal Year, Customer (5), Employee (7), Item (5), Test
Parameter (10, DocType custom di `starlab_lab_ops`) sudah ada.

---

## 1. Urutan Pembuatan DocType Stub

Field persis mengikuti instruksi awal (TSD Bagian 4) — tidak disederhanakan. Urutan
pembuatan ditentukan oleh dependency Link antar DocType (bukan urutan di instruksi asli):

1. **Document Master** (`starlab_quality`) — tidak bergantung DocType stub lain.
2. **Susulan:** tambahkan field `metode_uji` (Link → Document Master) ke **Test Parameter**
   yang sempat ditunda di Fase 1 (lihat catatan Fase 1) — sekarang target Link-nya sudah ada.
3. **Work Order Pengujian** + child **WO Parameter Detail** (`starlab_lab_ops`) — Link ke
   Customer, Quotation (DocType native ERPNext, sudah ada), Employee, Test Parameter (semua
   sudah ada).
4. **Sample** (`starlab_lab_ops`) — Link ke Work Order Pengujian.
5. **Test Result** + child **QC Detail** (`starlab_lab_ops`) — Link ke Sample, Work Order
   Pengujian, Test Parameter, Employee.
6. **LHU** + child **LHU Test Result Detail** (`starlab_lab_ops`) — Link ke Work Order
   Pengujian, Customer, Employee, Test Result.
7. **Petty Cash Entry** (`starlab_customizations`) — Link ke Employee, Journal Entry
   (native ERPNext). Tidak bergantung DocType stub lain, bisa dibuat kapan saja.

Semua 6 DocType stub: field `status` sebagai Select biasa (tanpa Workflow), **Track Changes
diaktifkan**, dibuat via script Python (`bench execute`) sama seperti Test Parameter di Fase 1,
lalu source hasil export disalin balik ke masing-masing folder app di repo ini.

---

## 2. Data Dummy (Bagian B instruksi awal)

Diseed lewat script Python idempotent, sama pola dengan seed Fase 1:

- 10 Work Order Pengujian (variasi status), masing-masing 2-4 baris WO Parameter Detail
- 20 Sample (variasi status, beberapa "Bisa Dibuang" dengan `tanggal_musnah` di masa lalu)
- 30 Test Result (variasi status termasuk Divalidasi/Ditolak, qc_detail terisi sebagian)
- 5 LHU berstatus Issued
- 5 Petty Cash Entry + beberapa Journal Entry manual pembanding
- 5 Sales Invoice (variasi due_date: overdue / jatuh tempo dekat / belum jatuh tempo)
- Beberapa Bank Transaction + Payment Entry (sebagian matched, sebagian belum)
- Stock Ledger Entry yang membuat stok Item di bawah Reorder Level
- 5 Document Master (variasi level & status) dengan Document Distribution ke beberapa divisi

---

## 3. Rencana Implementasi 10 Report

Rekomendasi tipe implementasi + alasan (dikonfirmasi ke user sebelum dibangun, sesuai
aturan interaksi wajib):

| # | Report | Tipe | Alasan |
|---|--------|------|--------|
| 1 | Rekap Work Order | **Script Report** | Perlu join Work Order Pengujian + child WO Parameter Detail dengan filter di kedua level (Customer/Status di parent, PJ Analis di child) — lebih rapi dikontrol lewat Python daripada SQL murni. |
| 2 | Status Sample Realtime | **Query Report** (SQL) | Single doctype, filter sederhana (Status/Matriks/WO). Color-coded status cukup pakai `formatter` di file `.js` report. |
| 3 | Rekap Hasil Uji per Parameter | **Script Report** | Butuh agregasi (rata-rata/jumlah per parameter-analis-periode) + output chart batang — natural di Script Report lewat return value `chart`. |
| 4 | Laporan Hasil Uji (LHU) Resmi | **Print Format** (bukan Report) | Ini dokumen cetak berkop surat untuk klien, bukan report tabel — pakai Print Format Jinja/HTML terpasang ke DocType LHU. Kop surat pakai placeholder dulu (logo & alamat dummy). |
| 5 | Laporan Keuangan Operasional | **Script Report** | Menggabungkan 2 sumber berbeda (Petty Cash Entry + Journal Entry) dengan kategorisasi — perlu logic Python untuk menyatukan & mengelompokkan. |
| 6 | Aging Piutang | **Pakai native ERPNext** — report **"Accounts Receivable"** / **"Accounts Receivable Summary"** | Sudah dicek: kedua report ini ada di `erpnext/accounts/report/`, sudah punya filter Customer/Party, Report Date, dan bucket aging (0-30/31-60/61-90/90+ hari) persis kebutuhan poin 6. Tidak perlu dibangun dari nol. |
| 7 | Rekonsiliasi Bank | **Pakai native ERPNext** — DocType tool **"Bank Reconciliation Tool"** + report **"Bank Reconciliation Statement"** | Sudah dicek: keduanya ada di `erpnext/accounts/doctype(report)/bank_reconciliation_*`. Tool untuk matching manual, report untuk lihat status reconciled/outstanding per akun bank & periode — sudah cukup. |
| 8 | Rekap Kepatuhan Dokumen Mutu | **Query Report** (SQL, join child table) | Document Master + child Document Distribution, filter Level/Status/Divisi — join 2 tabel lewat SQL cukup untuk kebutuhan ini. |
| 9 | Rekap Stok Reagen & Consumable | **Query Report** (SQL) | Item + Bin (stok saat ini) vs Reorder Level, filter Item Group/Warehouse, alert stok kritis lewat `formatter`. |
| 10 | Laporan Kinerja SLA Pengujian | **Script Report** | Perlu hitung selisih `target_pengujian` (WO Parameter Detail) vs tanggal aktual selesai (dari Sample/Test Result), lalu persentase keterlambatan per matriks/analis — murni logic Python, tidak feasible di SQL Query Report biasa. |

**Ringkasan native vs custom:**
- **Full native ERPNext** (tidak perlu dibangun): #6 Aging Piutang, #7 Rekonsiliasi Bank.
- **Print Format** (bukan report reguler): #4 LHU Resmi.
- **Script Report custom**: #1, #3, #5, #10.
- **Query Report custom**: #2, #8, #9.

Setiap report dites langsung (jalankan report, cek data dummy muncul sesuai filter) sebelum
lanjut ke report berikutnya — hasil uji dilaporkan per report.

---

## 4. Asumsi/Keputusan yang Diambil (perlu dikonfirmasi)

1. `metode_uji` di Test Parameter ditambahkan **setelah** Document Master dibuat (bukan dari
   awal Fase 1) — lihat poin 1 di atas.
2. Untuk report #6 dan #7, tidak membangun report baru — hanya memvalidasi bahwa native
   report/tool ERPNext sudah dipakai dan datanya muncul benar dengan data dummy kita.
3. Print Format LHU pakai kop surat **placeholder** (nama perusahaan + alamat dummy, tanpa
   logo asli) — sesuai catatan di instruksi awal.
4. Data dummy (nomor WO, nama sample, dsb.) dikarang representatif, bukan dari BRA.
