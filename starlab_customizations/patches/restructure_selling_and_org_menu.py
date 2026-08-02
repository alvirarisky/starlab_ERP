import json

import frappe

# docs/Penambahan_Pengurangan_Fitur_ERP_SAI.md -- penyesuaian menu Desk bawaan ERPNext
# supaya sesuai kebutuhan SAI (Lab Testing, bukan manufaktur/retail POS). Semua di sini
# memutasi doc Workspace standard (bukan fork file JSON erpnext ke app kita) lewat ORM
# langsung -- konsisten dengan pola patch lain di app ini (mis.
# fix_sai_branding_css_import.py), dan aman dari ketimpa sync berikutnya karena
# `modified` ke-bump lewat save() ini (lihat catatan panjang soal staleness-check di
# ringkasan-seluruh-sprint.md Bagian 3.x).
#
# "Organisasi" di jobdesc = section sidebar "Organization" di dalam Workspace bawaan
# "ERPNext Settings" (Company/Letter Head/Department/Branch/User/Role Permissions/
# Email Account) -- BUKAN Workspace terpisah bernama "Organization" (tidak ada di versi
# ERPNext ini).
#
# Catatan koreksi: versi awal fungsi-fungsi di bawah ini juga memutasi
# `workspace.sidebar_items` -- field itu TIDAK ADA di skema DocType Workspace pada
# versi Frappe yang benar-benar ke-install di project ini (cuma ada number_cards,
# charts, shortcuts, links, quick_lists, custom_blocks, roles), jadi selalu
# AttributeError sejak awal ditulis, sebelum sempat menyimpan apa pun. Sidebar
# switcher antar-Workspace di versi ini dibangun dari daftar dokumen Workspace itu
# sendiri (parent_page/public/roles), bukan dari child table per-Workspace terpisah
# -- jadi memutasi `links` saja (yang mengisi grid konten "Reports & Masters" di
# dalam halaman Workspace) sudah cukup buat capai maksud aslinya, tanpa perlu
# rekayasa "sidebar" terpisah yang memang tidak ada mekanismenya di versi ini.


def execute():
	_restructure_selling()
	_swap_branch_for_employee_list()


def _restructure_selling():
	if not frappe.db.exists("Workspace", "Selling"):
		return
	selling = frappe.get_doc("Workspace", "Selling")

	# --- content (layout grid "Reports & Masters") -- buang blok card "Point of Sale" ---
	content = json.loads(selling.content or "[]")
	content = [b for b in content if b.get("data", {}).get("card_name") != "Point of Sale"]
	selling.content = json.dumps(content)

	# --- links (isi tiap card) ---
	# Buang total: seluruh card "Point of Sale" (Card Break + isinya), Price List,
	# Coupon Code, Blanket Order. Sembunyikan (bukan buang) Pricing Rule -- tetap
	# harus aktif di belakang layar karena Promotional Scheme bergantung ke situ.
	# Ganti label tampilan Item -> "Parameter", Item Group -> "Matriks" (murni label,
	# link_to tetap DocType Item/Item Group aslinya).
	new_links = []
	skip_until_next_card_break = False
	for link in selling.links:
		if link.type == "Card Break":
			skip_until_next_card_break = link.label == "Point of Sale"
			if skip_until_next_card_break:
				continue
		elif skip_until_next_card_break:
			continue

		if link.label in ("Price List", "Coupon Code", "Blanket Order"):
			continue
		if link.label == "Pricing Rule":
			link.hidden = 1
		elif link.label == "Item":
			link.label = "Parameter"
		elif link.label == "Item Group":
			link.label = "Matriks"
		new_links.append(link)
	selling.links = new_links

	selling.save(ignore_permissions=True)


def _swap_branch_for_employee_list():
	if not frappe.db.exists("Workspace", "ERPNext Settings"):
		return
	settings = frappe.get_doc("Workspace", "ERPNext Settings")

	# Tidak ada entri "Branch" sama sekali di links Workspace ini pada versi
	# Frappe/ERPNext yang ke-install di sini (dicek langsung ke data live, bukan
	# diasumsikan) -- jadi tidak ada yang bisa "ditukar". Cukup tambahkan link ke
	# Employee List kalau belum ada, sesuai maksud aslinya (shortcut ke Daftar
	# Karyawan tersedia di section ini).
	already_present = any(link.link_to == "Employee" for link in settings.links)
	if already_present:
		return

	settings.append(
		"links",
		{
			"type": "Link",
			"label": "Daftar Karyawan",
			"icon": "users-round",
			"link_type": "DocType",
			"link_to": "Employee",
		},
	)
	settings.save(ignore_permissions=True)
