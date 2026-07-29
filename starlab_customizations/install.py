import frappe

# hooks.py::get_website_user_home_page -- landing page per role begitu
# login, supaya user non-IT tidak harus tahu dulu nama Workspace-nya
# sendiri buat pindah manual dari /desk generik. Diarahkan ke Workspace
# ROLE spesifik (bukan Workspace domain CRM/LIMS/Keuangan/Kualitas hasil
# nesting di Bagian 3.28) karena itu yang paling relevan buat kerja
# sehari-hari; domain overview tetap bisa diakses lewat expand Workspace
# picker.
#
# Nilai HARUS diawali "desk/" (bukan slug polos) -- login.js melakukan
# `window.location.href = data.home_page` dari halaman /login (path 1
# segmen), jadi resolusi URL relatif browser memperlakukan slug polos
# (mis. "manajer-teknis") sebagai SIBLING dari /login, mendarat di
# localhost:8000/manajer-teknis (404 "Page not found") alih-alih
# localhost:8000/desk/manajer-teknis yang benar. "desk/<slug>" (relatif,
# dua segmen) resolve dengan benar ke "/desk/<slug>" -- pola yang sama
# persis dipakai core Frappe sendiri untuk kasus System User default
# ("desk" polos, bukan "/desk", lihat frappe.website.utils.get_home_page).
ROLE_HOME_WORKSPACE = {
	"Direksi": "desk/direksi",
	"Marketing": "desk/marketing",
	"Administrasi": "desk/administrasi",
	"Finance": "desk/finance",
	"Laboratorium": "desk/laboratorium",
	"Manajer Teknis": "desk/manajer-teknis",
	"Manajer Mutu": "desk/manajer-mutu",
}


def get_home_page(user):
	# Administrator secara sintetis punya SEMUA role (lihat
	# frappe.permissions.get_roles()) -- kalau tidak dikecualikan, bakal
	# ke-redirect ke Workspace role PERTAMA yang match secara acak/tidak
	# terduga, alih-alih tetap di /desk generik seperti user admin
	# semestinya.
	if user == "Administrator":
		return None

	for role in frappe.get_roles(user):
		if role in ROLE_HOME_WORKSPACE:
			return ROLE_HOME_WORKSPACE[role]

	return None


# TSD Bagian 9: "Aging Piutang" dan "Rekonsiliasi Bank" sudah tercakup oleh
# report native ERPNext (Accounts Receivable, Bank Reconciliation Statement)
# -- tidak perlu report custom. Satu-satunya yang kurang: keduanya default
# hanya untuk role "Accounts Manager"/"Accounts User"/"Auditor", sementara
# proyek ini pakai role custom "Finance".
#
# Report ini "is_standard": Yes -- menyimpan perubahan langsung ke field
# `roles`-nya ditolak Frappe di luar developer_mode ("Standard reports can
# only be created in developer mode"). Mekanisme resmi Frappe untuk
# menambah role akses ke standard report/page tanpa developer_mode adalah
# DocType "Custom Role" -- tapi custom_roles yang ada MENGGANTI (bukan
# menambah) daftar roles report aslinya (lihat get_custom_allowed_roles di
# frappe/core/doctype/report/report.py), jadi role asli harus disalin ulang
# supaya Accounts Manager/Accounts User/Auditor tidak kehilangan akses.
FINANCE_REPORT_ACCESS = ["Accounts Receivable", "Bank Reconciliation Statement"]


def after_migrate():
	for report_name in FINANCE_REPORT_ACCESS:
		if not frappe.db.exists("Report", report_name):
			continue

		existing_roles = frappe.get_all("Custom Role", filters={"report": report_name}, limit=1)
		if existing_roles:
			custom_role = frappe.get_doc("Custom Role", existing_roles[0].name)
			if any(r.role == "Finance" for r in custom_role.roles):
				continue
			custom_role.append("roles", {"role": "Finance"})
		else:
			report = frappe.get_doc("Report", report_name)
			custom_role = frappe.new_doc("Custom Role")
			custom_role.report = report_name
			custom_role.ref_doctype = report.ref_doctype
			for r in report.roles:
				custom_role.append("roles", {"role": r.role})
			custom_role.append("roles", {"role": "Finance"})

		custom_role.save(ignore_permissions=True)
