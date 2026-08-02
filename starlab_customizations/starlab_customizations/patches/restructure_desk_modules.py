import frappe

# docs/Penambahan_Pengurangan_Fitur_ERP_SAI.md -- SAI tidak melakukan manufaktur, jadi
# 3 Workspace bawaan ERPNext ini (dan Subcontracting, yang ternyata cuma card DI DALAM
# Manufacturing, bukan Workspace terpisah) tidak relevan buat operasional Lab Testing.
#
# Field `is_hidden` bawaan DocType Workspace dipakai langsung -- BUKAN mekanisme
# "Workspace Customization" (frappe.desk.doctype.workspace_customization) yang
# sebelumnya dipakai di sini: DocType itu tidak ada di versi Frappe yang benar-benar
# ke-install di project ini (bench init --frappe-branch=version-16), jadi patch ini
# selalu ModuleNotFoundError sejak awal ditulis, gagal di `import`, sebelum sempat
# menjalankan apa pun di execute(). `is_hidden` field biasa di doc Workspace live-nya
# dipilih sebagai gantinya, dengan pola yang sama seperti parent_page di bawah: aman
# dari ketimpa sync berikutnya karena `modified` ke-bump lewat save(), sama seperti
# pola yang sudah dipakai berkali-kali di sesi sebelumnya untuk Workspace kita sendiri.
# `is_hidden=1` menyembunyikan dari sidebar/workspace switcher -- DocType & datanya di
# baliknya tetap fungsional penuh, cuma entry menunya yang hilang.
HIDDEN_WORKSPACES = ["Manufacturing", "Quality", "Stock"]


def execute():
	for workspace in HIDDEN_WORKSPACES:
		if not frappe.db.exists("Workspace", workspace):
			continue
		doc = frappe.get_doc("Workspace", workspace)
		if not doc.is_hidden:
			doc.is_hidden = 1
			doc.save(ignore_permissions=True)

	_reparent_assets_under_accounting()


def _reparent_assets_under_accounting():
	# Field ini diubah langsung di doc Workspace live-nya (aman dari ketimpa sync
	# berikutnya karena `modified` ke-bump lewat save() ini, sama seperti pola yang
	# sudah dipakai berkali-kali di sesi sebelumnya untuk Workspace kita sendiri).
	#
	# Target parent-nya "Keuangan", BUKAN "Accounting" -- versi Frappe/ERPNext yang
	# ke-install di project ini tidak punya Workspace bawaan bernama "Accounting"
	# sama sekali (cuma ada "Invoicing" & "Financial Reports" di module Accounts).
	# "Keuangan" adalah hub Workspace custom yang sudah dibuat terpisah untuk
	# project ini (module "Starlab Customizations", dipakai juga sebagai parent
	# Workspace "Finance") -- itu yang dimaksud "grup menu Accounting" di
	# docs/Penambahan_Pengurangan_Fitur_ERP_SAI.md.
	if not frappe.db.exists("Workspace", "Assets") or not frappe.db.exists("Workspace", "Keuangan"):
		return
	assets = frappe.get_doc("Workspace", "Assets")
	if assets.parent_page != "Keuangan":
		assets.parent_page = "Keuangan"
		assets.save(ignore_permissions=True)
