import frappe

# Letter Head TIDAK ada di frappe.model.sync.IMPORTABLE_DOCTYPES (beda dari
# Print Format/Workspace/Report yang otomatis di-reimport dari file JSON-nya
# tiap `bench migrate`) -- meskipun letter_head/<slug>/<slug>.json di app ini
# ditulis persis dengan format "standard": "Yes" yang sama seperti file-file
# module-sync itu. Akibatnya edit ke pt_starlab_analitik_indonesia.json (mis.
# menambahkan logo) TIDAK PERNAH otomatis kepakai di site manapun -- DB tetap
# menyimpan versi lama sampai ada yang secara eksplisit reload doc ini.
# Ditemukan saat menambahkan logo ke kop surat: file JSON sudah benar,
# `bench migrate` jalan tanpa galat, tapi print PDF LHU/Quotation tetap
# tampilkan versi tanpa logo sampai patch ini ditambahkan.
LETTER_HEAD_NAME = "pt_starlab_analitik_indonesia"


def execute():
	frappe.reload_doc("starlab_customizations", "letter_head", LETTER_HEAD_NAME, force=True)
