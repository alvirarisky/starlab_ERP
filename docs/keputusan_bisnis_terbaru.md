# Keputusan Bisnis Terbaru — Siap Dieksekusi

> **📁 ARSIP HISTORIS (per 2026-08-06):** Semua item di bawah sudah dieksekusi dan terserap ke `ringkasan-seluruh-sprint.md` (lihat Bagian 3.22/3.23) dan kode terkait. Dipertahankan sebagai catatan keputusan stakeholder, bukan daftar kerjaan aktif. Lihat `docs/OVERVIEW_PROJECT.md` untuk kondisi terkini.

Kumpulan jawaban dari stakeholder (dikumpulin 2026-07-30) buat item-item yang sebelumnya masih berstatus "menunggu jawaban" di `docs/BRA_v2.md` Bagian 14.6 dan `docs/ringkasan-seluruh-sprint.md` Bagian 5. Semua item di bawah ini sudah ada jawaban resmi — **boleh langsung dieksekusi, gak perlu nunggu konfirmasi lagi**, kecuali disebutkan lain.

Setelah dieksekusi, jangan lupa update juga `docs/BRA_v2.md`, `docs/PRD_v8.md`/`docs/TSD_v3.md`, dan `docs/ringkasan-seluruh-sprint.md` supaya keputusan ini tercatat resmi di dokumen acuan, bukan cuma di file ini.

---

## 1. Posisi Rush Fee di kalkulasi Total Invoice

**Jawaban:** Diskon cuma boleh kena ke bagian pengujian, Rush Fee TIDAK boleh ikut kediskon.

**Yang perlu diubah:** `starlab_customizations/starlab_customizations/quotation_hooks.py::_calculate_price_summary` — sekarang base perhitungan Discount pakai `base_after_rush_fee` (Sub Total + Rush Fee), harus diganti balik ke `doc.sub_total` saja (Rush Fee dihitung terpisah, tidak masuk base diskon). Lokasi ini sudah ditandai komentar di kode dari sebelumnya.

**Prioritas: tinggi** — ini soal duit, ada kemungkinan langsung mempengaruhi Quotation yang lagi dipakai.

---

## 2. Alur kerja Subkontraktor pengujian

**Jawaban:** Manajer Teknis minta ke Administrasi untuk buatkan form Work Order ke lab subkon. Form itu disetujui oleh Manajer Mutu dan Direktur. Untuk pemantauan progress, cukup mengacu ke estimasi hari kerja lab penguji eksternal, nanti hasilnya di-follow up oleh Administrasi.

**Yang perlu diubah:** `starlab_lab_ops/.../doctype/wo_parameter_detail/wo_parameter_detail.json` (field `status_pengujian`, opsi "Subkon") — sekarang cuma penanda status tanpa alur, deskripsi field yang bilang "belum ada alur kerja" perlu dihapus/diupdate begitu alurnya sudah diimplementasi. Perlu dirancang: form/alur pengajuan Work Order ke subkon, approval MM + Direktur, dan pencatatan estimasi waktu pengerjaan dari lab eksternal untuk keperluan follow-up Administrasi.

---

## 3. Masa retensi Sample sebelum dimusnahkan

**Jawaban:** Sample dimusnahkan 1 bulan setelah LHU terbit.

**Yang perlu diubah:** `starlab_lab_ops/.../doctype/sample/sample.json` (field `retensi`, `tanggal_musnah`) — sekarang diisi manual dengan catatan "belum ada kebijakan otomatis". Karena aturannya sekarang jelas, ini bisa diotomatisasi: `tanggal_musnah` dihitung otomatis = tanggal LHU terbit + 30 hari, alih-alih diisi manual. Deskripsi field yang bilang "belum ada kebijakan" perlu dihapus/diupdate.

---

## 4. Arah approval Work Order (siapa approve pekerjaan Manajer Teknis)

**Jawaban:** Bukan satu aturan tunggal, tergantung jenis approval-nya:
- Kerjaan teknis harian (raw data, hasil hitung) — tidak ada approval sampai manajemen puncak, cukup dari Penyelia ke Manajer Teknis.
- Pengadaan barang / kalibrasi — approval ke Manajer Mutu.
- LHU — pengesahan ke Direktur.
- Work Order ke subkontraktor eksternal — approval ke Manajer Mutu dan Direktur (lihat poin 2 di atas).
- Ada juga audit tahunan silang antara Teknis dan Mutu (Teknis audit Mutu, Mutu audit Teknis) — ini audit kepatuhan berkala, bukan approval per-transaksi.
- Kerjaan sehari-hari secara umum tidak butuh approval atasan, cuma beberapa form tertentu saja.

**Yang perlu dicek:** Workflow `Work Order Pengujian` yang sudah berjalan sekarang — perlu direview apakah state/transition yang ada sekarang sudah sesuai dengan pembagian di atas, atau perlu disesuaikan. Ini bukan langsung "ganti kode", tapi "cek dulu kesesuaiannya" sebelum memutuskan perlu perubahan atau tidak.

---

## 5. RACI dokumen "List Work Order"

**Jawaban:** Divisi yang terlibat: **Administrasi dan (Manajer) Teknis.**

**Yang perlu diubah:** Ini melengkapi jawaban poin 4 di atas — dipakai sebagai referensi tambahan saat review Workflow Work Order Pengujian.

---

## 6. Mapping Item master ke Quotation/Invoice

**Jawaban:** Rinci per parameter, bukan satu Item generik. Acuan format: contoh Quotation dan Invoice yang sudah dibuat Astri — harus memuat matriks, parameter, dan regulasi/acuan yang dipakai.

**Yang perlu diubah:** `Quotation Parameter Detail`, tombol "Buat Invoice" di LHU — sekarang auto-create Quotation/Invoice sengaja tidak mengisi tabel `items` karena belum ada mapping ini. Perlu dirancang mapping Test Parameter → Item (atau struktur setara) yang mencantumkan matriks, parameter, dan regulasi acuan di baris item.

---

## 7. Integrasi sistem Accurate

**Jawaban:** Otomatis (sinkron API), bukan input manual oleh Finance.

**Yang perlu diubah:** Belum ada kode sama sekali untuk ini — scope kerja baru. Perlu digali lebih lanjut ke Finance/Direksi: akses API Accurate seperti apa yang tersedia (dokumentasi API, kredensial), dan data apa saja yang perlu disinkronkan (Quotation yang sudah Approved saja, atau termasuk Invoice/Payment juga).

---

## 8. Format nomor Quotation

**Jawaban:** Ikuti format yang sudah berjalan di sistem sekarang (`Quo-SAI/[bulan romawi]/[tahun]/[nomor urut]`) — dikonfirmasi resmi, tidak ada perubahan.

**Yang perlu diubah:** Tidak ada — sudah sesuai implementasi saat ini, tinggal dicatat sebagai resmi (bukan asumsi lagi) di dokumen acuan.

---

## 9. Matriks akses data finansial (Rekening Koran & Mutasi Kas)

**Jawaban:** Tidak untuk semua divisi — hanya Finance dan Direksi yang boleh akses.

**Yang perlu diubah:** Role Permission untuk dokumen terkait Rekening Koran/Mutasi Kas (Bank Account, Bank Transaction, dll) — perlu direview supaya cuma role Finance dan Direksi yang punya akses baca, divisi lain dibatasi.

---

## 10. Detail kalibrasi & inventaris alat

**Jawaban:**
- Jadwal kalibrasi alat lab bervariasi per jenis alat: ada yang per tahun, per 2 tahun, atau per 3 tahun.
- Kalibrasi dikerjakan vendor eksternal — sistem cukup mencatat hasil uji kalibrasinya, tidak perlu detail proses kalibrasi itu sendiri.
- Alat kantor non-lab (AC, komputer, dll): pencatatan jadwal perawatan sifatnya opsional sesuai kebutuhan, tapi reminder per 3 bulan boleh diterapkan kalau mau.

**Yang perlu diubah:** Belum ada kode untuk modul Inventaris alat sama sekali (lihat `docs/TSD_v3.md` Bagian 4.13 untuk desain awal) — ini scope pengembangan baru, bukan perbaikan yang sudah ada.

---

## 11. Nama akun GL Kas Kecil — baru terjawab sebagian

**Jawaban:** Nama akun "Kas Kecil" dikonfirmasi. **Akun pasangannya untuk sisi pengeluaran (placeholder kode: "Beban Operasional Kantor") belum dikonfirmasi ulang** — masih perlu ditanyakan ke Finance kalau mau presisi, atau boleh dipakai dulu sebagai default sementara.

**Lokasi kode:** `starlab_customizations/petty_cash_hooks.py`.

---

## Masih belum ada jawaban (di luar scope eksekusi sekarang)

- **Jadwal wawancara langsung ke Direksi dan Marketing** — untuk melengkapi requirement gathering awal secara menyeluruh. Sengaja ditunda, bukan prioritas sekarang.
