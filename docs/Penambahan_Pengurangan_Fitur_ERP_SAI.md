# Penambahan & Pengurangan Fitur ERP

Catatan dari review manual, sudah diperjelas lewat diskusi (2026-07-30) supaya tidak ambigu saat dieksekusi.

## Organisasi
- Company — tetap
- Letter Head — tetap
- Department — tetap
- **Branch — shortcut menu dihapus, diganti shortcut menu Daftar Karyawan (Employee List)**. DocType Branch sendiri tidak perlu dihapus dari sistem, cuma tidak lagi ditampilkan sebagai shortcut di halaman Organisasi.
- User — tetap
- Role Permissions — tetap
- Email Account — tetap (daftar email untuk semua karyawan)

## Assets
- Semuanya dipindahkan ke dalam grup menu Accounting, tidak lagi jadi grup menu sendiri.

## Selling
- Semuanya tetap ada, dengan penyesuaian berikut:
- **POS — dihapus** dari menu.
- **Item — cuma ganti label tampilan jadi "Parameter"**. Ini murni perubahan nama/label, bukan perubahan fungsi — DocType Item tetap Item seperti biasa, cuma teks yang ditampilkan ke user diganti. *(Catatan: ini terpisah dari isu lama soal Test Parameter belum ditautkan ke Item master untuk Quotation/Invoice — isu itu tidak ikut terjawab lewat perubahan label ini, tetap dianggap open item terpisah.)*
- **Item Groups — cuma ganti label tampilan jadi "Matriks"**. Sama seperti Item di atas, murni ganti label, bukan ganti fungsi.
- **Price List — dihapus** dari menu.
- **Item Price — tetap**, tidak ada perubahan.
- **Pricing Rules — disembunyikan dari menu** (bukan dihapus/dimatikan fungsinya). Tetap harus aktif di belakang layar karena Promotional Scheme bergantung ke Pricing Rule secara teknis (Promotional Scheme otomatis membuat Pricing Rule saat disimpan) — kalau Pricing Rule benar-benar dihapus/dimatikan, Promotional Scheme ikut tidak berfungsi.
- **Promotional Scheme — tetap**, tidak ada perubahan.
- **Coupon Code — dihapus** dari menu.
- **Blanket (Blanket Order) — dihapus** dari menu.

## Project
- Semuanya tetap, dengan catatan:
  - **Project** — dipakai sebagai daftar project dari client.
  - **Task** — tidak ada perubahan. Catatan sebelumnya ("approval") merujuk ke sistem approval yang **sudah ada** lewat Workflow (Quotation, Work Order Pengujian, dll), bukan fitur baru yang perlu dibangun di Task — diabaikan, tidak perlu ditindaklanjuti.
  - **Time Sheet** — dipakai sebagai jadwal sampling.

## Buying
- Semuanya tetap.

## Manufacturing
- Dihapus total dari menu.

## Quality (bawaan ERPNext)
- Dihapus total dari menu. *(Ini modul Quality bawaan ERPNext untuk manufaktur — berbeda dari app custom `starlab_quality` yang sudah dibangun terpisah untuk Document Control ISO 17025, tidak saling terkait.)*

## Stock
- **Dihapus total** dari menu (bukan sekadar ganti label). Kebutuhan pelacakan bahan kimia consumable dan alat gelas sudah tercakup lewat menu LIMS yang sudah ada, jadi menu Stock bawaan ERPNext tidak diperlukan lagi sebagai grup menu terpisah.

## Subcontract (bawaan ERPNext)
- Dihapus total dari menu. *(Ini modul Subcontracting bawaan ERPNext untuk manufaktur — berbeda dari status "Subkon" di Work Order Pengujian, yang soal kirim sample ke laboratorium eksternal dan statusnya masih Open Question terpisah (F0-5), tidak saling terkait.)*
