# Dependency Install Order — `starlab_quality` sebelum `starlab_lab_ops`

**Status:** Ditemukan saat audit sebelum Sprint 5 (lihat `docs/audit-sebelum-sprint-5.md`), dan sudah diperbaiki di kode.

## Masalah

`starlab_lab_ops/starlab_lab_ops/doctype/test_parameter/test_parameter.json` punya field:

```json
{
  "fieldname": "metode_uji",
  "fieldtype": "Link",
  "label": "Metode Uji",
  "options": "Document Master"
}
```

`Document Master` adalah DocType milik app **`starlab_quality`**, bukan `starlab_lab_ops`. Field ini sudah tertanam langsung di `test_parameter.json` (bukan lagi Custom Field runtime) — artinya setiap `bench migrate`/fresh install yang men-sync DocType `Test Parameter` **membutuhkan `Document Master` sudah ada lebih dulu**, atau akan gagal dengan `WrongOptionsDoctypeLinkError`.

Sebelum perbaikan ini, `starlab_lab_ops/hooks.py` mendeklarasikan `required_apps = ["erpnext"]` saja — **tidak** menyertakan `starlab_quality`. Site dev saat ini (`sites/starlab-erp.localhost/site_config.json` → `installed_apps`) bahkan sudah ter-install dengan urutan `starlab_lab_ops` **sebelum** `starlab_quality` di `apps.txt`. Ini hanya "selamat" di environment dev saat ini karena field `metode_uji` awalnya ditambahkan lewat migration script terpisah (`setup/add_metode_uji_field.py`) yang dijalankan manual **setelah** `starlab_quality`/`Document Master` sudah ada di DB — bukan karena dependency-nya benar-benar terjamin oleh mekanisme app install Frappe.

## Perbaikan

`starlab_lab_ops/starlab_lab_ops/hooks.py`:

```python
required_apps = ["erpnext", "starlab_quality"]
```

Dengan `required_apps` ini, `bench install-app starlab_lab_ops` di instance/site baru akan otomatis meng-install `starlab_quality` lebih dulu jika belum ada, sehingga urutan install tidak lagi bergantung pada ingatan/disiplin manual.

## Yang perlu diperhatikan ke depan

- Site dev yang sudah ada (`starlab-erp.localhost`) **tidak perlu di-reinstall** — datanya sudah konsisten (Document Master sudah ada duluan secara kebetulan). Perbaikan ini terutama untuk **instance baru** (staging/produksi/dev environment baru).
- Kalau ke depan ada field lain di `starlab_lab_ops` atau `starlab_customizations` yang Link ke DocType custom app lain, terapkan pola yang sama: tambahkan app pemilik DocType tujuan ke `required_apps`.
- `starlab_customizations` dan `starlab_quality` sendiri masih punya `required_apps = []` (di-comment) — belum ada cross-dependency lain yang diketahui saat ini, tapi perlu dicek ulang tiap kali menambah Link field lintas-app.
