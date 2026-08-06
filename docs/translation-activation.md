# Aktivasi Translation (Bahasa Indonesia)

**Status:** Item TSD Sprint 5 "Aktivasi fitur Translation untuk lokalisasi label UI Bahasa Indonesia" — riset selesai, tidak perlu kode tambahan.

## Temuan

Semua label field/DocType custom SAI (Client Inquiry, Quotation custom field, Work Order Pengujian, dsb.) sudah ditulis **langsung dalam Bahasa Indonesia** di `label` masing-masing (bukan translation key). Mekanisme translation Frappe (`_()`, `Translation` DocType, file `.po`/`.mo`) hanya berlaku untuk string yang dilewatkan lewat `_()` — string Indonesia yang sudah literal seperti ini tidak butuh lookup translation apa pun, jadi "mengaktifkan Translation" **tidak berdampak sama sekali** ke label-label custom SAI, dengan atau tanpa diaktifkan.

Yang benar-benar terpengaruh: **chrome bawaan Frappe/ERPNext** — tombol ("Save", "Submit", "Cancel", "Amend"), sidebar/menu desk, pesan validasi bawaan, label field core sebelum di-custom (mis. "Customer", "Status" versi asli). Bench ini **sudah** punya `id.po`/`id.mo` terkompilasi untuk `frappe` dan `erpnext` (`sites/assets/locale/id/LC_MESSAGES/{frappe,erpnext}.mo`) — jadi terjemahan untuk bagian ini **sudah tersedia**, tinggal diaktifkan.

## Cara mengaktifkan

**2026-08-06: keputusan dibalik.** Semula `System Settings.language` sengaja dibiarkan murni manual (lihat alasan lama di bawah) — tapi di lapangan itu berarti site-wide default balik ke `en` setiap kali site dibuat ulang dari nol (rebuild Docker, setup ulang buat tester baru, dst.), karena tidak ada apa pun yang menjaganya. Sekarang diotomatisin: `starlab_customizations.install.after_migrate` → `_ensure_indonesian_language()` men-set `System Settings.language = "id"` setiap `bench migrate`, idempoten (skip kalau sudah `id`).

1. Otomatis: **System Settings → Language** akan selalu `Indonesian` (`id`) setelah `bench migrate` — tidak perlu diset manual lagi.
2. Opsional per-user: **User → Language** = `Indonesian`, kalau user tertentu mau override default site (atau balik ke `English` khusus akunnya sendiri).
3. Kalau ada string core yang masih belum terjemahan sempurna, override lewat **Desk → Translation** (DocType `Translation`) — isi `Language`, `Source Text`, `Translated Text` — tanpa perlu ubah kode apa pun.

<details>
<summary>Alasan lama (sebelum 2026-08-06) kenapa ini tidak diotomatisin</summary>

Kami sengaja tidak menambahkan `after_install`/`after_migrate` hook yang memaksa `System Settings.language = "id"` secara otomatis dari kode `starlab_customizations` — itu setting site-wide yang semestinya jadi keputusan sadar operator/administrator saat setup, bukan dipaksakan diam-diam oleh satu custom app bisnis.

</details>
