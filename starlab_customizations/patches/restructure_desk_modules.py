import frappe
from frappe.desk.doctype.workspace_customization.workspace_customization import (
	upsert_property_customization,
)

# docs/Penambahan_Pengurangan_Fitur_ERP_SAI.md -- SAI tidak melakukan manufaktur, jadi
# 3 Workspace bawaan ERPNext ini (dan Subcontracting, yang ternyata cuma card DI DALAM
# Manufacturing, bukan Workspace terpisah) tidak relevan buat operasional Lab Testing.
# Dipakai "Workspace Customization" (mekanisme resmi Frappe buat override tampilan
# Workspace standard tanpa menyentuh file aslinya -- lihat
# frappe/desk/doctype/workspace_customization/) alih-alih hapus/edit langsung filenya,
# supaya tidak konflik/ketimpa tiap kali erpnext sendiri di-update. `visibility="Hidden"`
# menyembunyikan dari sidebar/workspace switcher untuk semua user KECUALI role
# "Workspace Manager" -- DocType & datanya di baliknya tetap fungsional penuh, cuma
# entry menunya yang hilang.
HIDDEN_WORKSPACES = ["Manufacturing", "Quality", "Stock"]


def execute():
	for workspace in HIDDEN_WORKSPACES:
		if frappe.db.exists("Workspace", workspace):
			upsert_property_customization(workspace, visibility="Hidden")

	_reparent_assets_under_accounting()


def _reparent_assets_under_accounting():
	# parent_page bukan bagian dari facet yang didukung Workspace Customization
	# (cuma visibility/icon/warna/urutan/roles) -- untuk nesting, field ini harus
	# diubah langsung di doc Workspace live-nya (aman dari ketimpa sync berikutnya
	# karena `modified` ke-bump lewat save() ini, sama seperti pola yang sudah
	# dipakai berkali-kali di sesi sebelumnya untuk Workspace kita sendiri).
	if not frappe.db.exists("Workspace", "Assets"):
		return
	assets = frappe.get_doc("Workspace", "Assets")
	if assets.parent_page != "Accounting":
		assets.parent_page = "Accounting"
		assets.save(ignore_permissions=True)
