import frappe

# TSD/audit housekeeping (docs/audit/LAPORAN_AUDIT.md D-4/L-3): 5 Role Profile
# bawaan ERPNext dan puluhan Role bawaan erpnext/hrms tidak dipakai satupun
# oleh user manapun di sistem ini (hanya 7 role bisnis + "HR" custom yang
# dipakai) -- warisan install yang tidak relevan buat operasional lab
# testing, berpotensi bikin admin baru salah pilih Role/Role Profile.
UNUSED_ROLE_PROFILES = ["Purchase", "Sales", "Accounts", "Manufacturing", "Inventory"]

# Role dasarnya beda dari Role Profile: ratusan DocType bawaan erpnext/hrms
# mereferensikan Role ini langsung di DocPerm-nya sendiri (bagian dari
# fixture app tsb) -- bench migrate berikutnya otomatis membuat ulang Role
# apa pun yang masih disebut di situ. Hard delete jadi PERCUMA untuk Role
# yang masih direferensikan permission bawaan itu (bakal muncul lagi tiap
# migrate); disabled=1 adalah satu-satunya cara yang benar-benar bertahan
# (frappe.get_roles() mengabaikan role disabled, jadi efeknya "tidak
# dipakai" tanpa terus-menerus fighting migrate). Role yang benar-benar
# orphan (tidak direferensikan permission apa pun) tetap dihapus permanen.
KEEP_ROLES = {
	"Direksi", "Manajer Teknis", "Manajer Mutu", "Finance", "Marketing",
	"Administrasi", "Laboratorium", "HR",
	"Administrator", "Guest", "All", "System Manager", "Desk User", "Customer", "Supplier",
}


def execute():
	_delete_unused_role_profiles()
	_cleanup_unused_roles()


def _delete_unused_role_profiles():
	# Role Profile bukan fixture DocType manapun (bukan cuma tidak ada di
	# fixtures kita -- erpnext/hrms sendiri juga tidak mereferensikannya dari
	# DocPerm apa pun), jadi aman dihapus permanen: tidak akan dibuat ulang
	# oleh bench migrate berikutnya.
	for name in UNUSED_ROLE_PROFILES:
		if not frappe.db.exists("Role Profile", name):
			continue
		if frappe.db.exists("User", {"role_profile_name": name}):
			continue
		frappe.delete_doc("Role Profile", name, ignore_permissions=True)


def _cleanup_unused_roles():
	unused_candidates = frappe.get_all("Role", filters={"name": ["not in", list(KEEP_ROLES)]}, pluck="name")
	for role in unused_candidates:
		if frappe.db.exists("Has Role", {"role": role, "parenttype": "User"}):
			continue

		if frappe.db.exists("DocPerm", {"role": role}) or frappe.db.exists("Custom DocPerm", {"role": role}):
			if not frappe.db.get_value("Role", role, "disabled"):
				frappe.db.set_value("Role", role, "disabled", 1)
			continue

		try:
			frappe.delete_doc("Role", role, ignore_permissions=True)
		except frappe.LinkExistsError:
			# Masih direferensikan dokumen lain (Workflow/Report/Page/dst) di
			# luar DocPerm/Custom DocPerm -- aman diabaikan, disable saja
			# supaya tidak terus dicoba dihapus tiap migrate.
			frappe.db.set_value("Role", role, "disabled", 1)
