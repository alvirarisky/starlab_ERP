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

	# --- sidebar_items (nav kiri) -- section "POS" dibuang total (Section Break +
	# semua child-nya), Price List/Coupon Code/Blanket Order/Pricing Rule dibuang dari
	# section "Items & Pricing" (sidebar tidak punya flag "hidden" per-item seperti
	# links, jadi buang = cara satu-satunya buat "sembunyikan" di sini), label Item &
	# Item Group ikut diganti biar konsisten dengan links di atas.
	new_sidebar = []
	in_pos_section = False
	for item in selling.sidebar_items:
		if item.type == "Section Break":
			in_pos_section = item.label == "POS"
			if in_pos_section:
				continue
		elif in_pos_section:
			continue

		if item.label in ("Price List", "Coupon Code", "Blanket Order", "Pricing Rule"):
			continue
		if item.label == "Item" and item.link_to == "Item":
			item.label = "Parameter"
		elif item.label == "Item Group":
			item.label = "Matriks"
		new_sidebar.append(item)
	selling.sidebar_items = new_sidebar

	selling.save(ignore_permissions=True)


def _swap_branch_for_employee_list():
	if not frappe.db.exists("Workspace", "ERPNext Settings"):
		return
	settings = frappe.get_doc("Workspace", "ERPNext Settings")

	found_branch = False
	for item in settings.sidebar_items:
		if item.label == "Branch" and item.link_to == "Branch":
			item.label = "Daftar Karyawan"
			item.link_to = "Employee"
			item.icon = "users-round"
			found_branch = True
			break

	if found_branch:
		settings.save(ignore_permissions=True)
