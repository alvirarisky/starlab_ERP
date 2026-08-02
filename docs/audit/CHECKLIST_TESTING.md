# Checklist Ringkas — Siap Testing Besok (2026-08-03)

Diurutkan Critical → Low. Lihat `docs/audit/LAPORAN_AUDIT.md` untuk detail/lokasi kode lengkap tiap item.

> **Update 2026-08-02 malam:** Semua item Critical/High/Medium yang sifatnya kode (bukan keputusan bisnis/UX manual) **sudah di-fix dan sudah di-`bench migrate` + restart ke instance Docker yang lagi jalan (`starlab.local`)**, lalu diverifikasi ulang lewat simulasi permission live. Perubahan kode ada di working tree, **belum di-commit** (sesuai aturan repo — commit dilakukan manual oleh tim). Jalankan `git status`/`git diff` untuk review sebelum commit. Checklist di bawah sudah disesuaikan: item yang sudah beres ditandai ✅, sisanya murni verifikasi visual/manual atau butuh keputusan tim.

## Sebelum sesi testing dimulai (lakukan pagi ini)

- [ ] **[CRITICAL]** Umumkan ke seluruh tester: pakai akun `<role>.test@example.com` (password `Test@12345`) untuk role-play, **JANGAN** pakai `test.<role>@starlab.local` — akun itu ikut punya `System Manager`, hasil uji RBAC-nya tidak valid. *(Ini soal akun/proses, bukan kode — tidak bisa saya "fix", cuma bisa diumumkan.)*
- [x] ✅ **[CRITICAL — FIXED]** `/status-klien` (Client Portal): LHU sekarang punya Custom DocPerm read-only untuk role Customer (`starlab_lab_ops/fixtures/custom_docperm.json`), plus row-level scoping baru (`lhu_hooks.get_permission_query_conditions`/`has_permission`) supaya Customer cuma bisa baca LHU milik company-nya sendiri, bukan company lain. Sudah di-migrate + diverifikasi (`get_perms_for(["Customer"], "Custom DocPerm")` mengembalikan permission `read`). **Tetap coba login sebagai user Customer sungguhan besok** untuk verifikasi visual halamannya, karena saya tidak bisa cek tampilan browser dari sini.
- [ ] **[HIGH]** Review & commit seluruh perubahan uncommitted di repo (baik yang sudah ada sebelumnya — `restructure_desk_modules.py`, `restructure_selling_and_org_menu.py`, `seed_test_users.py` — maupun ~25 file hasil fix audit ini). Semuanya sudah terbukti jalan di container live, tapi akan hilang kalau container di-rebuild sebelum di-commit.

## Test case eksplisit yang tetap wajib dicoba saat sesi (verifikasi hasil fix, bukan cuma klik-klik biasa)

- [x] ✅ **[CRITICAL — FIXED]** Administrasi tidak lagi punya `submit` mentah di Quotation (`custom_docperm.json`, di-set `submit: 0`) — diverifikasi live: `frappe.has_permission("Quotation","submit", user=administrasi)` sekarang `False`. Approval final cuma bisa lewat Direksi di ujung rantai Workflow. **Tetap worth dicoba manual besok** sebagai regression check.
- [x] ✅ **[CRITICAL — FIXED]** Rush Fee sudah TIDAK ikut kena Discount lagi (`quotation_hooks.py::_calculate_price_summary` diubah sesuai `docs/keputusan_bisnis_terbaru.md` #1) — diverifikasi dengan simulasi angka (Sub Total 1.000.000, Rush Fee 100%, Discount 10% → DPP sekarang 1.900.000, sebelumnya salah 1.710.000). Teks catatan "ASUMSI kerja belum dikonfirmasi" juga sudah dihapus dari print PDF. **Coba buat 1 Quotation dengan Rush Fee+Discount aktif besok untuk konfirmasi visual di print.**
- [x] ✅ **[CRITICAL — FIXED]** Direksi sekarang punya akses read ke Bank Account/Bank Transaction/Bank Reconciliation Tool/Bank Statement Import (Custom DocPerm baru ditambahkan, sesuai keputusan bisnis 30 Juli poin 9) — diverifikasi live.
- [ ] **[HIGH — PERLU DICOBA MANUAL]** Buat Quotation baru dari nol lewat UI form standar (bukan auto-create dari Client Inquiry/Kaji Ulang Tender) → pastikan tidak crash saat save. *(Catatan: kode test `test_quotation_with_client_inquiry_succeeds` di `test_quotation_fields.py` mengindikasikan alur normal via `make_quotation()` test util MENGISI tabel Items dengan 1 baris dummy, jadi kemungkinan besar TIDAK crash di UI normal — tapi saya tidak sempat 100% reproduksi kondisi UI asli, jadi tetap masukkan ke smoke test besok.)*
- [x] ✅ **[HIGH — FIXED]** Ke-5 laporan LIMS (Laporan Kinerja SLA Pengujian, Rekap Hasil Uji per Parameter, Rekap Stok Reagen dan Consumable, Rekap Work Order, Status Sample Realtime) + Laporan Keuangan Operasional + Rekap Kepatuhan Dokumen Mutu sekarang punya role bisnis yang relevan (bukan cuma System Manager) — diverifikasi live lewat `frappe.get_doc("Report", ...).roles`. **Coba buka masing-masing sebagai role terkait besok untuk verifikasi visual.**
- [x] ✅ **[HIGH — FIXED]** `notify_role_via_whatsapp` sekarang dibatasi ke role System Manager/Direksi/Manajer Mutu (`frappe.only_for(...)`) — user biasa yang coba panggil endpoint ini sekarang kena `PermissionError` (diverifikasi live dengan akun Marketing). Notifikasi WhatsApp otomatis dari alur bisnis (SLA, approval pending, dst.) tetap jalan normal karena dipisah ke fungsi internal terpisah yang tidak lewat endpoint HTTP ini.
- [x] ✅ **[MEDIUM — FIXED]** Manajer Mutu tidak lagi punya `delete` di Document Master, Laboratorium tidak lagi punya `delete` di Test Result, Administrasi tidak lagi punya `delete` di Petty Cash Entry — ketiganya `is_submittable=0` jadi sebelumnya bisa dihapus permanen meski sudah lewat approval. Sekarang cuma read/write/create; koreksi data draft dilakukan lewat edit, bukan delete.

## Backlog perbaikan — sudah dikerjakan juga (scope diperluas atas permintaan)

- [x] ✅ **[MEDIUM — FIXED]** N+1 query di scheduled tasks (`starlab_customizations/tasks.py`, `starlab_lab_ops/tasks.py`, `lhu_hooks.py::populate_test_result_list`, `document_control_hooks.py::_notify_distribution`) — sekarang di-cache/di-batch per role atau per-parameter dalam satu run, bukan satu query per baris lagi.
- [x] ✅ **[LOW — FIXED]** `LIMIT` ditambahkan ke 9 custom report yang pakai raw SQL (3 `starlab_customizations`, 5 `starlab_lab_ops`, 1 `starlab_quality`). Untuk `Laporan Keuangan Operasional` yang punya kalkulasi saldo berjalan, LIMIT diterapkan dengan hati-hati (ambil jendela transaksi terbaru + opening balance tetap dihitung dari SUM sebelum jendela itu) supaya saldo tidak jadi salah.
- [x] ✅ **[LOW — FIXED]** Teks catatan internal di print format `Quotation Ringkasan Harga` sudah dihapus (lihat item Rush Fee di atas).

## Masih perlu keputusan/konfirmasi TIM (bukan sesuatu yang bisa saya putuskan sepihak)

- [ ] **[MEDIUM]** Apakah semua 7 role memang boleh membuat/mengedit Document Master untuk divisinya sendiri (desain saat ini, tidak diubah), atau harus dipusatkan ke Manajer Mutu saja.
- [ ] **[MEDIUM]** Apakah 4 Workspace domain (CRM, LIMS, Keuangan, Kualitas) memang harus terlihat oleh SEMUA role (saat ini `roles: []`, tanpa restriksi, tidak diubah), atau perlu dibatasi ke role terkait.
- [ ] **[MEDIUM]** Auto-transition status (`db_set`/`set_value` di `wo_hooks.py`, `quotation_hooks.py`, `lhu_hooks.py`) tidak tercatat di Version/Track Changes log — perlu dipikirkan sebelum go-live produksi (kepentingan audit trail ISO 17025). Tidak diubah (butuh keputusan desain, bukan sekadar bugfix).
- [ ] **[LOW]** Rapikan Role/Role Profile bawaan ERPNext yang tidak dipakai (Purchase, Sales, Accounts, Manufacturing, Inventory Role Profile; puluhan Role bawaan tidak relevan) — tidak diubah, murni housekeeping opsional.

## Hal yang perlu diverifikasi manual oleh tim (di luar kapasitas saya)

- [ ] Responsiveness/layout visual di berbagai ukuran layar — saya tidak punya akses browser untuk cek ini.
- [ ] Kualitas visual print PDF (kop surat, margin, dst.) — LHU Print Format sebelumnya diketahui masih pakai kop surat placeholder (perlu dicek apakah sudah final).
- [ ] Verifikasi visual seluruh item yang saya tandai ✅ FIXED di atas — saya sudah verifikasi lewat simulasi permission/kalkulasi di backend (bukan tebakan), tapi belum pernah lihat langsung di browser.
