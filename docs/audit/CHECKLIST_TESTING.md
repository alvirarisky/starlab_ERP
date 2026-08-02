# Checklist Ringkas — Siap Testing Besok (2026-08-03)

Diurutkan Critical → Low. Lihat `docs/audit/LAPORAN_AUDIT.md` untuk detail/lokasi kode lengkap tiap item.

## Sebelum sesi testing dimulai (lakukan pagi ini)

- [ ] **[CRITICAL]** Umumkan ke seluruh tester: pakai akun `<role>.test@example.com` (password `Test@12345`) untuk role-play, **JANGAN** pakai `test.<role>@starlab.local` — akun itu ikut punya `System Manager`, hasil uji RBAC-nya tidak valid.
- [ ] **[CRITICAL]** Cek `/status-klien` (Client Portal) dengan user Customer sungguhan sebelum sesi mulai — dugaan kuat halaman ini error karena LHU tidak punya permission untuk role Customer sama sekali. Kalau benar error, ini blocker untuk semua skenario client-facing.
- [ ] **[HIGH]** Commit 3 file yang saat ini uncommitted di repo (`restructure_desk_modules.py`, `restructure_selling_and_org_menu.py`, `seed_test_users.py`) — fix di dalamnya sudah terbukti jalan di container live, tapi akan hilang kalau container di-rebuild sebelum di-commit.

## Test case eksplisit yang wajib dicoba saat sesi (bukan cuma klik-klik biasa)

- [ ] **[CRITICAL]** Sebagai Administrasi, coba submit sebuah Quotation Draft **lewat API/console langsung** (bukan tombol UI "Ajukan"/"Setujui") — cek apakah approval chain MT→MM→Direksi benar-benar terlewati. Kalau berhasil ter-submit, ini bypass RBAC nyata (lihat Laporan bagian B-2).
- [ ] **[CRITICAL]** Buat 1 Quotation dengan Rush Fee **dan** Discount aktif bersamaan → cek Total Invoice di print PDF. Sesuai keputusan bisnis 30 Juli, Rush Fee **tidak boleh** ikut kena diskon. Kalau kalkulasi masih memotong Rush Fee, ini bug uang yang sudah dikonfirmasi tapi belum di-fix (kode: `quotation_hooks.py::_calculate_price_summary`).
- [ ] **[CRITICAL]** Login sebagai Direksi, coba buka Bank Account / Bank Transaction / Bank Reconciliation Tool → seharusnya BISA (sesuai keputusan bisnis 30 Juli poin 9), tapi saat ini kemungkinan besar 403 karena belum ada Custom DocPerm untuk role Direksi.
- [ ] **[HIGH]** Buat Quotation baru dari nol lewat UI form standar (bukan auto-create dari Client Inquiry/Kaji Ulang Tender) → pastikan tidak crash saat save (ada indikasi potensi `TypeError` di kalkulasi `base_in_words` kalau tabel "Items" bawaan ERPNext kosong).
- [ ] **[HIGH]** Login sebagai Laboratorium/Manajer Teknis/Manajer Mutu/Direksi, coba buka salah satu dari 5 laporan LIMS (Laporan Kinerja SLA Pengujian, Rekap Hasil Uji per Parameter, Rekap Stok Reagen dan Consumable, Rekap Work Order, Status Sample Realtime) dan Finance coba buka "Laporan Keuangan Operasional" — semuanya kemungkinan besar akan menolak akses ("Not Permitted") karena role-nya cuma `System Manager`.
- [ ] **[HIGH]** Sebagai role apapun yang login (bukan admin), coba panggil method `notify_role_via_whatsapp` (via `/api/method/starlab_integrations.whatsapp.notify_role_via_whatsapp`) dengan role="Direksi" — cek apakah benar-benar terkirim tanpa ada pengecekan otorisasi tambahan.
- [ ] **[MEDIUM]** Sebagai Manajer Mutu, coba `delete` sebuah Document Master yang statusnya "Aktif" — pastikan tim sadar ini secara teknis bisa dilakukan (tidak ada proteksi docstatus di DocType non-submittable).

## Backlog perbaikan (tidak menghalangi testing besok, tapi catat)

- [ ] **[HIGH]** `Administrasi`/`Laboratorium`/`Manajer Mutu` punya `delete` pada Petty Cash Entry/Test Result/Document Master yang sudah lewat tahap approval — pertimbangkan cabut `delete` atau batasi hanya untuk state awal (Draft).
- [ ] **[MEDIUM]** Konfirmasi tim: apakah semua 7 role memang boleh membuat/mengedit Document Master untuk divisinya sendiri (desain saat ini), atau harus dipusatkan ke Manajer Mutu saja.
- [ ] **[MEDIUM]** Konfirmasi tim: apakah 4 Workspace domain (CRM, LIMS, Keuangan, Kualitas) memang harus terlihat oleh SEMUA role (saat ini `roles: []`, tanpa restriksi), atau perlu dibatasi ke role terkait.
- [ ] **[MEDIUM]** Auto-transition status (`db_set`/`set_value` di `wo_hooks.py`, `quotation_hooks.py`, `lhu_hooks.py`) tidak tercatat di Version/Track Changes log — perlu dipikirkan sebelum go-live produksi (kepentingan audit trail ISO 17025).
- [ ] **[LOW]** Hapus paragraf catatan internal ("ASUMSI kerja ... belum dikonfirmasi ke PO") dari print format `Quotation Ringkasan Harga` — sudah basi sejak keputusan 30 Juli keluar, dan seharusnya tidak pernah muncul di dokumen client-facing sejak awal.
- [ ] **[LOW]** Rapikan Role/Role Profile bawaan ERPNext yang tidak dipakai (Purchase, Sales, Accounts, Manufacturing, Inventory Role Profile; puluhan Role bawaan tidak relevan) supaya tidak membingungkan saat setup user baru.
- [ ] **[LOW]** Perbaiki N+1 query di scheduled tasks (`tasks.py` kedua app) dan tambahkan `LIMIT`/pagination di 8 custom report yang pakai raw SQL — tidak berdampak untuk data testing kecil, tapi jadi utang teknis untuk skala produksi.

## Hal yang perlu diverifikasi manual oleh tim (di luar kapasitas saya)

- [ ] Responsiveness/layout visual di berbagai ukuran layar — saya tidak punya akses browser untuk cek ini.
- [ ] Kualitas visual print PDF (kop surat, margin, dst.) — LHU Print Format sebelumnya diketahui masih pakai kop surat placeholder (perlu dicek apakah sudah final).
