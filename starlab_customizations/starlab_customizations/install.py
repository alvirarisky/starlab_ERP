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
	# 2026-08-03: Workspace "Laboratorium" dihapus, digabung ke "LIMS" --
	# kontennya sudah nyaris superset Laboratorium dari awal (Work Order,
	# Sample, Test Result, LHU semua sudah ada di sana), jadi role Laboratorium
	# diarahkan langsung ke LIMS alih-alih punya Workspace kosong terpisah.
	# LIMS sendiri sekarang dibatasi roles ke Laboratorium + Manajer Teknis
	# saja (sebelumnya publik/tanpa batasan role sebagai "domain overview").
	"Laboratorium": "desk/lims",
	"Manajer Teknis": "desk/manajer-teknis",
	"Manajer Mutu": "desk/manajer-mutu",
	"HR": "desk/hr",
}


@frappe.whitelist()
def get_my_workspace_route():
	# Dipanggil dari public/js/redirect_to_role_workspace.js -- get_home_page()
	# di bawah cuma dipakai Frappe core untuk redirect SEKALI seusai submit
	# form /login (lihat komentar di ROLE_HOME_WORKSPACE di atas). Kalau
	# session sudah aktif (cookie belum di-clear) dan user buka /app atau
	# /desk langsung tanpa lewat form login lagi, redirect itu tidak pernah
	# kepanggil sama sekali -- SPA cuma nampilin Workspace publik default
	# apa adanya. Endpoint ini dipanggil dari client tiap kali Desk baru
	# dibuka supaya perilakunya konsisten juga untuk kasus itu.
	return get_home_page(frappe.session.user)


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


# 2026-08-02: ditemukan role bisnis (Marketing, Laboratorium, dkk) bisa lihat
# sejumlah Workspace bawaan ERPNext/Frappe yang murni buat admin teknis (Build
# = DocType/Workflow builder, Users = manajemen user & permission, dst) --
# ini semua Workspace `roles: []` (tidak dibatasi sama sekali) sejak awal.
# Dibatasi ke System Manager saja di sini (bukan `is_hidden`, supaya System
# Manager/Administrator tetap bisa akses) -- dijalankan di after_migrate
# (bukan patch sekali-jalan) karena Workspace bawaan ERPNext/Frappe ini
# ke-reload/reset tiap `bench migrate` menjalankan sync module app
# masing-masing, beda dari Workspace milik app kita sendiri yang aman dari
# re-sync begitu `modified` ke-bump lewat save().
SYSTEM_MANAGER_ONLY_WORKSPACES = [
	"Build", "Users", "Website", "Support", "Integrations",
	"Selling", "Invoicing", "Financial Reports",
	# 2026-08-03: 8 Workspace bawaan app `hrms` (github.com/frappe/hrms) --
	# sama seperti Workspace bawaan ERPNext di atas, ini juga `roles: []`
	# (tidak dibatasi) begitu di-install, jadi kelihatan ke SEMUA role
	# termasuk yang non-HR. Kita pakai 1 Workspace "HR" custom sendiri
	# (starlab_customizations/.../workspace/hr/) sebagai satu-satunya
	# dashboard HR, konsisten dengan pola role lain di project ini --
	# 8 Workspace bawaan ini didisain ulang cakupannya ke System Manager
	# saja, bukan dihapus/is_hidden, supaya tetap bisa dibuka manual kalau
	# ada kebutuhan admin/debug yang butuh tampilan asli hrms.
	"Expenses", "HR Setup", "Leaves", "Recruitment",
	"Shift & Attendance", "Payroll", "Tax & Benefits",
	# "Performance" & "Tenure" TIDAK di sini -- 2026-08-03 dikonfirmasi gak
	# kepake sama sekali, jadi disembunyikan total lewat is_hidden (lihat
	# FULLY_HIDDEN_WORKSPACES di bawah), bukan cuma dibatasi ke System Manager.
	# "Home"/"ERPNext Settings" (module "Setup") baru kelihatan bocor sejak
	# role "HR" ditambahkan -- role HR ini yang pertama dari 7 role bisnis
	# yang punya akses ke DocType bermodule "Setup" (Employee), jadi baru
	# sekarang celah modul "Setup" ini kena.
	"Home", "ERPNext Settings",
]


def _restrict_admin_workspaces_to_system_manager():
	# 2026-08-03: ketahuan Workspace `roles`/`is_hidden` di bawah TIDAK cukup
	# -- ada mekanisme grid ikon terpisah, DocType "Desktop Icon" (dulu
	# "modules"), yang punya `roles`/`hidden` SENDIRI, independen dari
	# Workspace meski nama record-nya sama persis. Selama ini fix di atas
	# cuma nutup switcher Workspace (sidebar/API get_workspaces), grid ikon
	# klasik ini tetap kebuka lebar ke semua role -- makanya dibenerin dua
	# doctype sekaligus di sini, bukan cuma Workspace.
	for name in SYSTEM_MANAGER_ONLY_WORKSPACES:
		if frappe.db.exists("Workspace", name):
			doc = frappe.get_doc("Workspace", name)
			if not (any(r.role == "System Manager" for r in doc.roles) and len(doc.roles) == 1):
				doc.roles = []
				doc.append("roles", {"role": "System Manager"})
				doc.save(ignore_permissions=True)

		if frappe.db.exists("Desktop Icon", name):
			icon = frappe.get_doc("Desktop Icon", name)
			if not (any(r.role == "System Manager" for r in icon.roles) and len(icon.roles) == 1):
				icon.roles = []
				icon.append("roles", {"role": "System Manager"})
				icon.save(ignore_permissions=True)


# docs/Penambahan_Pengurangan_Fitur_ERP_SAI.md -- keputusan resmi "dihapus
# total dari menu" untuk 3 Workspace bawaan ERPNext ini (SAI tidak manufaktur).
# "Performance"/"Tenure" (bawaan app hrms) ditambahkan 2026-08-03 dengan
# alasan sama -- dikonfirmasi gak kepake sama sekali. Re-assert di sini juga
# (bukan cuma di patch restructure_desk_modules untuk 3 yang pertama) untuk
# alasan yang sama seperti SYSTEM_MANAGER_ONLY_WORKSPACES di atas -- ketahuan
# ke-reset balik ke is_hidden=0 setelah beberapa kali migrate, kemungkinan
# besar sync module app masing-masing (erpnext/hrms) menimpanya lagi.
FULLY_HIDDEN_WORKSPACES = ["Manufacturing", "Quality", "Stock", "Performance", "Tenure"]


def _rehide_unused_workspaces():
	# Sama seperti _restrict_admin_workspaces_to_system_manager di atas --
	# Workspace.is_hidden sendirian tidak cukup, Desktop Icon (grid ikon)
	# punya field `hidden` + `roles` terpisah yang juga harus disentuh.
	for name in FULLY_HIDDEN_WORKSPACES:
		if frappe.db.exists("Workspace", name):
			doc = frappe.get_doc("Workspace", name)
			if not doc.is_hidden:
				doc.is_hidden = 1
				doc.save(ignore_permissions=True)

		if frappe.db.exists("Desktop Icon", name):
			icon = frappe.get_doc("Desktop Icon", name)
			changed = False
			if not icon.hidden:
				icon.hidden = 1
				changed = True
			if not (any(r.role == "System Manager" for r in icon.roles) and len(icon.roles) == 1):
				icon.roles = []
				icon.append("roles", {"role": "System Manager"})
				changed = True
			if changed:
				icon.save(ignore_permissions=True)


# 2026-08-03: sidebar kiri (panel navigasi di dalam halaman Workspace, BUKAN
# rail ikon app) TERNYATA dirender dari DocType terpisah "Workspace Sidebar"
# (+ child "Workspace Sidebar Item"), bukan dari field `sidebar_items` di
# JSON Workspace (field itu ada di schema tapi tidak dipakai render sama
# sekali di versi Frappe ini -- field mati). Role lain (Finance/Direksi/dst)
# punya record ini karena entah auto-generated atau dibuat manual oleh
# developer sebelumnya lewat UI -- BUKAN via fixture/file (`standard: 0`,
# tidak ada file sumbernya sama sekali), jadi "HR" yang baru dibuat hari ini
# tidak otomatis dapat. Dibuat idempoten di sini (bukan fixture) meniru pola
# yang sama seperti Workspace Sidebar role lain, supaya sidebar kiri
# Workspace "HR" tidak kosong.
HR_SIDEBAR_ITEMS = [
	("Home", "Workspace", "HR"),
	("Employee", "DocType", "Employee"),
	("Attendance", "DocType", "Attendance"),
	("Leave", "DocType", "Leave Application"),
	("Payroll", "DocType", "Payroll Entry"),
	("Training", "DocType", "Training Event"),
	("Performance", "DocType", "Appraisal"),
]


def _ensure_hr_workspace_sidebar():
	if not frappe.db.exists("Workspace", "HR"):
		return

	if frappe.db.exists("Workspace Sidebar", "HR"):
		sidebar = frappe.get_doc("Workspace Sidebar", "HR")
		existing_links = {item.link_to for item in sidebar.items}
	else:
		sidebar = frappe.new_doc("Workspace Sidebar")
		sidebar.title = "HR"
		existing_links = set()

	changed = not frappe.db.exists("Workspace Sidebar", "HR")
	for label, link_type, link_to in HR_SIDEBAR_ITEMS:
		if link_to in existing_links:
			continue
		# after_migrate ini jalan tiap ada `bench migrate` -- termasuk yang
		# dipanggil di tengah-tengah `bench new-site --install-app erpnext
		# --install-app hrms --install-app ... --install-app
		# starlab_customizations ...` (satu perintah, banyak app). Kalau
		# giliran ini kepanggil sebelum DocType dari hrms (Attendance, Leave
		# Application, dst) benar-benar ke-sync ke database -- pernah
		# kejadian di salah satu device -- link_type Workspace aman (Workspace
		# "HR" sudah dicek di atas), tapi link_type DocType ke DocType yang
		# belum ada bikin _validate_links() gagal dan menjatuhkan SELURUH
		# `bench new-site`, bukan cuma langkah kecil ini. Lewati item yang
		# DocType-nya belum ada sekarang -- ke-skip bukan permanen, karena
		# fungsi ini idempoten dan jalan lagi di `bench migrate` berikutnya
		# (termasuk yang saya panggil eksplisit di docker/start.sh), begitu
		# DocType-nya sudah ada, item ini otomatis nyusul ditambahkan.
		if link_type == "DocType" and not frappe.db.exists("DocType", link_to):
			continue
		sidebar.append(
			"items",
			{"label": label, "type": "Link", "link_type": link_type, "link_to": link_to, "collapsible": 1},
		)
		changed = True

	if changed:
		sidebar.save(ignore_permissions=True)


def _ensure_setup_complete():
	# 2026-08-04: root cause dari keluhan "sidebar kosong" DAN "kadang gak bisa
	# klik apa-apa / halaman putih kosong / gak bisa logout" pas testing --
	# bukan soal timing render, bukan soal redirect. frappe.ui.Sidebar
	# (frappe/public/js/frappe/ui/sidebar/sidebar.js, constructor) return
	# LANGSUNG tanpa pernah bikin this.wrapper sama sekali kalau
	# frappe.boot.setup_complete falsy -- artinya seluruh sidebar Desk bawaan
	# gak pernah ke-render buat SIAPAPUN di instance ini. Nilai itu dihitung
	# server-side lewat frappe.is_setup_complete() (frappe/__init__.py): cek
	# field is_setup_complete di Installed Application utk app "frappe" dan
	# "erpnext" -- field itu CUMA keisi kalau Setup Wizard interaktif
	# ERPNext dijalankan sampai selesai. Project ini sengaja skip Setup
	# Wizard (Company dibikin manual, lihat panduan setup) supaya nama/negara
	# Company bisa dikontrol persis -- konsekuensinya field itu gak pernah
	# ke-set, jadi sidebar bawaan Frappe rusak buat SEMUA orang dari awal.
	# Company yang sudah ada = sinyal paling jujur bahwa "setup" project ini
	# sudah selesai (meski bukan lewat wizard), jadi tandai lengkap di sini.
	if not frappe.db.exists("Company"):
		return
	for name in frappe.get_all(
		"Installed Application",
		filters={"app_name": ["in", ["frappe", "erpnext"]], "is_setup_complete": 0},
		pluck="name",
	):
		frappe.db.set_value("Installed Application", name, "is_setup_complete", 1)


def after_migrate():
	_ensure_setup_complete()
	_restrict_admin_workspaces_to_system_manager()
	_rehide_unused_workspaces()
	_ensure_hr_workspace_sidebar()

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
