# Jobdesc: Developer (Backend/Full-Stack) — Pira

Dokumen ini berisi tanggung jawab teknis untuk anggota tim yang ikut coding, menyesuaikan kondisi project ERP SAI saat ini (per `docs/ringkasan-seluruh-sprint.md` versi terbaru).

---

## Ringkasan Peran

Fokus utama: menutup technical debt yang sudah teridentifikasi, jadi penanggung jawab perbaikan bug begitu UAT mulai berjalan, dan mengeksekusi keputusan bisnis begitu turun dari stakeholder terkait.

---

## Tanggung Jawab Utama

### 1. Tutup gap test coverage — ✅ selesai (lihat `docs/ringkasan-seluruh-sprint.md` Bagian 3.26)

4 DocType di `starlab_customizations` yang tadinya stub kosong (`IntegrationTestCase` tanpa method `test_*`) sekarang punya 17 test beneran, semua lolos:

- `kaji_ulang_tender` (6 test)
- `tnc_master_template` (3 test)
- `client_inquiry` (4 test)
- `petty_cash_entry` (4 test)

Satu temuan penting muncul saat menulis test `kaji_ulang_tender`: auto-create Quotation Draft (`client_inquiry_hooks._create_quotation_draft`) ternyata **selalu gagal secara graceful** saat ini, bukan cuma untuk kasus Customer belum tertaut — karena belum ada mapping Item master (ini item yang SAMA dengan baris "Mapping Item master ke Quotation/Invoice" di Bagian 3 di bawah, masih menunggu keputusan PO). Test-nya sengaja MENGUNCI perilaku degradasi anggun ini sebagai baseline, bukan memperbaikinya sendiri tanpa konfirmasi.

Jalankan dengan:
```bash
bench --site <NAMA_SITE> run-tests --app starlab_customizations
```

### 2. Penanggung jawab bug dari UAT

7 akun test per role (Direksi, Marketing, Administrasi, Finance, Laboratorium, Manajer Teknis, Manajer Mutu — lihat `starlab_lab_ops/README.md`) sudah bisa dipakai di semua device. Begitu anggota tim non-coding mulai eksplorasi/nulis buku panduan pakai akun-akun itu, laporan bug atau perilaku yang gak sesuai ekspektasi ditampung dan diperbaiki di sini.

### 3. Eksekusi keputusan bisnis begitu dikonfirmasi

Item-item ini masih menunggu jawaban dari stakeholder (lihat `docs/PRD_v8.md` Bagian 10 dan `docs/BRA_v2.md`) — **jangan diimplementasikan berdasarkan tebakan sebelum ada konfirmasi eksplisit**:

| Keputusan yang ditunggu | Lokasi kode yang kena dampak |
|---|---|
| Posisi Rush Fee — sebelum/sesudah Discount dihitung | `starlab_customizations/starlab_customizations/quotation_hooks.py::_calculate_price_summary` |
| Alur kerja Subkontraktor (status "Subkon") | `starlab_lab_ops/.../doctype/wo_parameter_detail/wo_parameter_detail.json` (field `status_pengujian`) |
| Masa retensi Sample sebelum dimusnahkan | `starlab_lab_ops/.../doctype/sample/sample.json` (field `retensi`, `tanggal_musnah`) |
| Arah approval Work Order: MT ↔ Administrasi (Fase 0 F0-1) | Workflow `Work Order Pengujian` |
| Mapping Item master ke Quotation/Invoice | `Quotation Parameter Detail`, tombol "Buat Invoice" di LHU |
| Integrasi Accurate — API otomatis atau input manual Finance | Belum ada kode sama sekali, tunggu kejelasan cakupan dulu |

### 4. WhatsApp Gateway — penyambungan akhir

Kerangka sudah siap di `starlab_integrations` (WhatsApp Settings, provider Fonnte/Twilio/WhatsApp Business API). Begitu provider dipilih dan kredensial asli tersedia: isi WhatsApp Settings, aktifkan, dan uji kirim pesan sungguhan.

### 5. Sinkronisasi branch `app-starlab-*` ke Docker/CI

**Ini bagian yang paling sering kelewat** — `docker/apps.json` dan CI (`.github/workflows/ci.yml`) tidak membangun langsung dari `develop`, tapi dari branch terpisah per app (`app-starlab-lab-ops`, `app-starlab-customizations`, `app-starlab-quality`, `app-starlab-integrations`). Tiap kali ada commit di `develop` yang menyentuh salah satu app, branch itu harus di-update manual:

```bash
git subtree split --prefix=<nama_app> -b <nama_app>-new
git branch -f app-<nama_app> <nama_app>-new
git branch -D <nama_app>-new
git push --force origin app-<nama_app>
```

Kalau ini kelewat, device/CI lain akan build dari kode versi lama tanpa ada error yang jelas — sudah beberapa kali kejadian. Perlu disepakati eksplisit siapa yang pegang tanggung jawab ini di tiap sesi kerja.

### 6. (Opsional, prioritas rendah) Query Report custom untuk Dashboard — ✅ selesai (lihat `docs/ringkasan-seluruh-sprint.md` Bagian 3.27)

Beberapa metrik TSD (saldo kas real-time, conversion rate Quotation→WO, histori order per klien) sengaja belum dibuatkan Number Card karena butuh Query Report custom biar angkanya gak menyesatkan.

- **Saldo kas real-time** — ternyata sudah tercakup oleh report "Laporan Keuangan Operasional" yang sudah ada (baris paling atas = saldo saat ini), jadi tidak dibuatkan report baru.
- **Conversion rate Quotation→WO** — report baru "Konversi Quotation ke Work Order" (rekap per bulan).
- **Histori order per klien** — report baru "Histori Order per Klien" (satu baris per Customer).

---

## Alur Kerja & Referensi

- **Dokumen acuan wajib dibaca**: `docs/BRA_v2.md`, `docs/PRD_v8.md`, `docs/TSD_v3.md`, `docs/ringkasan-seluruh-sprint.md`. Kalau mengerjakan sesuatu yang mengubah keputusan/asumsi kerja sebelumnya, update juga dokumen ini biar histori keputusan gak hilang.
- **Sebelum push**: jalankan test app yang disentuh (`bench --site <NAMA_SITE> run-tests --app <nama_app>`), pastikan lolos.
- **Sebelum implementasi item di Bagian 3**: pastikan ada konfirmasi eksplisit tertulis dari stakeholder terkait, bukan asumsi sendiri — kalau perlu, catat dulu di dokumen PRD/BRA sebagai keputusan resmi sebelum mulai coding.

---

## Koordinasi

- **Pemegang repo utama**: eskalasi buat keputusan yang butuh persetujuan atau tidak jelas arahnya.
- **2 anggota tim non-coding**: sumber laporan bug & feedback UAT — lihat `jobdesc-pembuat-buku-panduan.md` di root repo untuk peran salah satunya.
- **Stakeholder bisnis** (Direksi, Finance, Laboratorium, Manajer Mutu, Manajer Teknis): sumber jawaban untuk item Bagian 3 dan Open Questions di `PRD_v8.md`.

---

## Ukuran Keberhasilan

- ✅ 4 DocType di Bagian 1 punya test yang beneran jalan & lolos.
- Laporan bug dari UAT direspon & diperbaiki dalam waktu wajar, bukan menumpuk.
- Begitu ada keputusan bisnis baru turun, implementasinya jalan tanpa banyak delay — dan dokumen PRD/BRA ikut diupdate.
- Branch `app-starlab-*` tidak pernah tertinggal lebih dari beberapa hari dari `develop`.

---

## Tambahan (2026-07-30)

### 7. Eksekusi restrukturisasi menu Desk (Penambahan & Pengurangan Fitur) — ✅ selesai (lihat `docs/ringkasan-seluruh-sprint.md` Bagian 3.29)

Catatan review manual soal menu Desk (`docs/Penambahan_Pengurangan_Fitur_ERP_SAI.md`) sudah diperjelas lewat diskusi — semua poin yang tadinya ambigu sudah dikonfirmasi, jadi **sudah siap dieksekusi**, gak perlu nunggu keputusan apa-apa lagi:

- **Organisasi**: shortcut Branch dihapus, diganti shortcut Daftar Karyawan (Employee List).
- **Selling**: hapus POS, Price List, Coupon Code, Blanket dari menu. Item → label tampilan diganti "Parameter" (murni ganti label, DocType & fungsinya tetap Item seperti biasa). Item Groups → label tampilan diganti "Matriks" (sama, murni label). Pricing Rules disembunyikan dari menu tapi **jangan dimatikan fungsinya** (Promotional Scheme bergantung ke situ di belakang layar).
- **Project**: tidak ada perubahan (catatan "Task = approval" di draf sebelumnya sudah diklarifikasi diabaikan — approval yang dimaksud sudah ada lewat Workflow terpisah).
- **Assets**: dipindahkan jadi bagian dari grup menu Accounting, bukan grup menu sendiri.
- **Manufacturing, Quality (bawaan ERPNext), Subcontract (bawaan ERPNext)**: dihapus total dari menu. *(Bukan `starlab_quality` custom app — itu tetap ada, tidak tersentuh. Juga bukan status "Subkon" di Work Order Pengujian — itu masih Open Question terpisah F0-5, tidak tersentuh.)*
- **Stock**: dihapus total dari menu (bukan ganti nama) — kebutuhan consumable/alat gelas sudah tercakup lewat menu LIMS yang sudah ada.

Detail lengkap & alasan tiap poin ada di `docs/Penambahan_Pengurangan_Fitur_ERP_SAI.md` itu sendiri — baca dulu sebelum mulai, supaya konteksnya jelas dan tidak salah eksekusi.

### 8. Update: 6 keputusan bisnis di Bagian 3 sudah terjawab semua

Semua item di tabel "Eksekusi keputusan bisnis" (Bagian 3 di atas) sekarang sudah ada jawaban resmi dari stakeholder — **siap dieksekusi, tidak perlu menunggu konfirmasi lagi**. Detail lengkap tiap jawaban + lokasi kode yang kena dampak ada di `docs/keputusan_bisnis_terbaru.md` — baca dulu sebelum mulai.

Ringkasan per item (detail lengkap ada di dokumen itu):

- **Posisi Rush Fee** — Discount cuma boleh mengurangi bagian pengujian, Rush Fee TIDAK ikut terdiskon. Prioritas tinggi karena soal duit.
- **Alur Subkontraktor** — sudah ada alur approval-nya (Manajer Teknis → Administrasi buat form → disetujui Manajer Mutu & Direktur, monitoring lewat estimasi hari kerja lab eksternal + follow up Administrasi), tapi masih perlu dirancang jadi fitur beneran, bukan cuma status penanda seperti sekarang.
- **Masa retensi Sample** — 1 bulan setelah LHU terbit, bisa diotomatisasi (`tanggal_musnah` dihitung otomatis, tidak perlu diisi manual lagi).
- **Arah approval Work Order** — ternyata bercabang tergantung jenis kerjaan (teknis harian, pengadaan/kalibrasi, LHU, subkon), bukan satu aturan tunggal — perlu direview dulu kesesuaiannya terhadap Workflow "Work Order Pengujian" yang sudah berjalan sebelum memutuskan perlu perubahan atau tidak.
- **Mapping Item master** — rinci per parameter (harus memuat matriks, parameter, regulasi acuan), bukan 1 Item generik. Acuan formatnya: contoh Quotation/Invoice yang sudah dibuat Astri.
- **Integrasi Accurate** — dikonfirmasi otomatis (API), bukan input manual. Ini scope pengembangan baru, belum ada kode sama sekali — perlu digali lebih lanjut soal akses API yang tersedia.

Satu catatan tambahan di luar Bagian 3: nama akun GL "Kas Kecil" juga sudah dikonfirmasi Finance, tapi akun pasangannya (placeholder "Beban Operasional Kantor") belum — lihat `docs/keputusan_bisnis_terbaru.md` poin 11.
