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
	"Build",
	"Users",
	"Website",
	"Support",
	"Integrations",
	"Selling",
	"Invoicing",
	"Financial Reports",
	# 2026-08-03: 8 Workspace bawaan app `hrms` (github.com/frappe/hrms) --
	# sama seperti Workspace bawaan ERPNext di atas, ini juga `roles: []`
	# (tidak dibatasi) begitu di-install, jadi kelihatan ke SEMUA role
	# termasuk yang non-HR. Kita pakai 1 Workspace "HR" custom sendiri
	# (starlab_customizations/.../workspace/hr/) sebagai satu-satunya
	# dashboard HR, konsisten dengan pola role lain di project ini --
	# 8 Workspace bawaan ini didisain ulang cakupannya ke System Manager
	# saja, bukan dihapus/is_hidden, supaya tetap bisa dibuka manual kalau
	# ada kebutuhan admin/debug yang butuh tampilan asli hrms.
	"Expenses",
	"HR Setup",
	"Leaves",
	"Recruitment",
	"Shift & Attendance",
	"Payroll",
	"Tax & Benefits",
	# "Performance" & "Tenure" TIDAK di sini -- 2026-08-03 dikonfirmasi gak
	# kepake sama sekali, jadi disembunyikan total lewat is_hidden (lihat
	# FULLY_HIDDEN_WORKSPACES di bawah), bukan cuma dibatasi ke System Manager.
	# "Home"/"ERPNext Settings" (module "Setup") baru kelihatan bocor sejak
	# role "HR" ditambahkan -- role HR ini yang pertama dari 7 role bisnis
	# yang punya akses ke DocType bermodule "Setup" (Employee), jadi baru
	# sekarang celah modul "Setup" ini kena.
	"Home",
	"ERPNext Settings",
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


# 2026-08-18: Workspace Sidebar (lihat komentar _ensure_hr_workspace_sidebar
# di atas) untuk Administrasi/Direksi/Marketing sudah lama ada duluan (dibuat
# manual lewat UI sebelum Workspace "CRM Starlab" ini ada), jadi otomatis
# TIDAK ikut kebentuk ulang begitu CRM Starlab baru ditambahkan -- 3 role
# yang punya akses ke CRM Starlab (lihat roles di
# workspace/crm_starlab/crm_starlab.json) jadi tidak punya jalan klik
# langsung ke sana dari sidebar mereka sendiri, cuma bisa lewat ketik URL
# manual. Ditambahkan idempoten di sini, bukan di file Workspace itu sendiri,
# karena field `shortcuts` (yang biasanya dipakai) tidak mendukung
# link_type/type "Workspace" sama sekali (cuma DocType/Report/Page/
# Dashboard/URL) -- satu-satunya jalur yang mendukung link ke Workspace lain
# adalah Workspace Sidebar Item ini.
CRM_STARLAB_SIDEBAR_TARGETS = ["Administrasi", "Direksi", "Marketing"]


def _ensure_crm_starlab_shortcuts():
	if not frappe.db.exists("Workspace", "CRM Starlab"):
		return

	for workspace_name in CRM_STARLAB_SIDEBAR_TARGETS:
		if not frappe.db.exists("Workspace Sidebar", workspace_name):
			continue

		sidebar = frappe.get_doc("Workspace Sidebar", workspace_name)
		if any(item.link_to == "CRM Starlab" for item in sidebar.items):
			continue

		max_idx = max([item.idx for item in sidebar.items], default=0)
		sidebar.append(
			"items",
			{
				"label": "CRM Starlab",
				"link_to": "CRM Starlab",
				"link_type": "Workspace",
				"type": "Link",
				"idx": max_idx + 1,
			},
		)
		sidebar.save(ignore_permissions=True)


COMPANY = "Starlab Analitik Indonesia"
COMPANY_ABBR = "SAI"


def _ensure_warehouse_type(name):
	# Company.on_update() (erpnext/setup/doctype/company/company.py,
	# create_default_warehouses) always tries to create a "Goods In Transit"
	# warehouse tagged with Warehouse Type "Transit" -- that Warehouse Type
	# record is normally seeded by ERPNext's Setup Wizard fixture install
	# (erpnext/setup/setup_wizard/operations/install_fixtures.py), which this
	# project deliberately never runs. Without it, creating Company below
	# fails with "Could not find Warehouse Type: Transit" (confirmed by
	# actually creating a from-scratch site and hitting this live). Same
	# pattern as _ensure_territory in starlab_lab_ops/setup/
	# seed_fase1_master_data.py -- a Setup-Wizard-only fixture, pre-created
	# by hand instead.
	if not frappe.db.exists("Warehouse Type", name):
		frappe.get_doc({"doctype": "Warehouse Type", "name": name}).insert(ignore_permissions=True)


def _ensure_company():
	# 2026-08-05: every other part of this project (patches, seed scripts,
	# _ensure_setup_complete right below) assumes a Company already exists --
	# but until this function, nothing in the codebase actually CREATED one.
	# `bench new-site` (what docker/start.sh uses) does not create a Company
	# at all -- that only happens via ERPNext's interactive Setup Wizard.
	# Consequence: anyone opening the browser before a human manually creates
	# the Company gets auto-redirected by Frappe core to /app/setup-wizard,
	# and actually completing that wizard (rather than skipping it) trips an
	# ERPNext bug of its own (install_fixtures.py's get_preset_records
	# accesses country.replace(...) while country is None) -- exactly the
	# error a tester ran into. Company is created here automatically instead,
	# so Setup Wizard should never come up for anyone again.
	if frappe.db.exists("Company", COMPANY):
		return
	_ensure_warehouse_type("Transit")
	frappe.get_doc(
		{
			"doctype": "Company",
			"company_name": COMPANY,
			"abbr": COMPANY_ABBR,
			"default_currency": "IDR",
			"country": "Indonesia",
			"chart_of_accounts": "Standard",
		}
	).insert(ignore_permissions=True)
	frappe.db.set_default("company", COMPANY)
	frappe.db.set_value("Global Defaults", None, "default_company", COMPANY)


def _ensure_fiscal_year():
	# ERPNext does NOT auto-create a Fiscal Year when a Company is created
	# (unlike the Chart of Accounts, which Company.on_update generates on its
	# own) -- without one, most transactions (Quotation, Sales Invoice, dst)
	# fail validation with no Fiscal Year covering their date. Full calendar
	# year (Jan 1 - Dec 31) of whatever year this instance happens to be set
	# up in -- not a hardcoded year, so this stays correct whenever this
	# project gets cloned/run.
	year = frappe.utils.getdate(frappe.utils.nowdate()).year
	fy_name = str(year)
	if frappe.db.exists("Fiscal Year", fy_name):
		return
	frappe.get_doc(
		{
			"doctype": "Fiscal Year",
			"year": fy_name,
			"year_start_date": f"{year}-01-01",
			"year_end_date": f"{year}-12-31",
		}
	).insert(ignore_permissions=True)


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
	# Wizard sepenuhnya (_ensure_company di atas bikin Company otomatis)
	# supaya nama/negara Company bisa dikontrol persis -- konsekuensinya
	# field itu gak pernah ke-set lewat jalur normal, jadi sidebar bawaan
	# Frappe rusak buat SEMUA orang dari awal kalau tidak ditandai manual di
	# sini. Company yang sudah ada = sinyal paling jujur bahwa "setup"
	# project ini sudah selesai (meski bukan lewat wizard).
	#
	# 2026-08-05: was `frappe.db.exists("Company")` (no second arg) -- that
	# does NOT mean "does any Company exist". frappe.db.exists(dt, dn=None)
	# with dn omitted checks `dt == dn` as a name lookup, which is always
	# false for a real doctype name like "Company" -- this function was a
	# silent no-op from the moment it was written. Found by actually
	# creating a from-scratch site and observing frappe.is_setup_complete()
	# stay False even after a real Company existed.
	# frappe.db.a_row_exists(doctype) is the real "does any row exist" check.
	if not frappe.db.a_row_exists("Company"):
		return
	for name in frappe.get_all(
		"Installed Application",
		filters={"app_name": ["in", ["frappe", "erpnext"]], "is_setup_complete": 0},
		pluck="name",
	):
		frappe.db.set_value("Installed Application", name, "is_setup_complete", 1)


def _ensure_indonesian_language():
	# 2026-08-06: lihat docs/translation-activation.md -- terjemahan Bahasa
	# Indonesia buat chrome bawaan Frappe/ERPNext (tombol, menu, pesan
	# validasi bawaan) sudah tersedia (id.po/id.mo terkompilasi ada di
	# sites/assets/locale/id/), tapi sebelumnya SENGAJA tidak diaktifkan lewat
	# kode (dianggap keputusan sadar operator, bukan sesuatu yang harus
	# dipaksakan satu custom app bisnis). Konsekuensinya di lapangan:
	# System Settings.language site-wide balik ke default "en" tiap kali site
	# dibuat ulang dari nol, karena tidak ada apa pun yang menjaganya --
	# dikonfirmasi kejadian berulang. Dibalik keputusannya di sini supaya
	# default-nya konsisten Bahasa Indonesia tanpa perlu diset ulang manual
	# tiap kali site di-provision. User yang belum punya field `language`
	# sendiri terisi (mayoritas -- tidak ada satu baris pun di codebase ini
	# yang pernah mengisinya) otomatis ikut default site ini.
	if frappe.db.get_single_value("System Settings", "language") == "id":
		return
	frappe.db.set_single_value("System Settings", "language", "id")


SAI_APP_LOGO = "/assets/starlab_customizations/images/sai-logo.png"
SAI_FAVICON = "/assets/starlab_customizations/images/sai-favicon.png"


def _ensure_sai_branding():
	# 2026-08-13: patches/set_sai_branding.py sets these once at patch time,
	# but Website Settings.favicon/app_logo were found back to None on a
	# long-lived dev site months later -- patches never re-run once logged
	# in Patch Log, so whatever reset them (most likely erpnext/hrms own
	# fixture sync touching the Website Settings single doc on a later
	# `bench migrate`, same class of drift as _ensure_indonesian_language
	# and the Workspace resets below) silently undid it for good. Re-assert
	# every migrate instead, same idempotent pattern as the rest of this file.
	website_settings = frappe.get_single("Website Settings")
	changed = False
	if website_settings.app_logo != SAI_APP_LOGO:
		website_settings.app_logo = SAI_APP_LOGO
		changed = True
	if website_settings.favicon != SAI_FAVICON:
		website_settings.favicon = SAI_FAVICON
		changed = True
	if changed:
		website_settings.save(ignore_permissions=True)


def _ensure_tnc_master_templates():
	# 2026-08-14: patches/seed_tnc_master_template.py and _v2.py are each
	# idempotent ("insert only if missing"), but a patch itself only ever
	# EXECUTES once (tracked in Patch Log) -- if the record it created goes
	# missing afterwards (observed on this long-lived dev site: both v01 and
	# v02 gone despite Patch Log showing both patches already ran, no
	# Deleted Document trace either; this is also one of the 7 CI test
	# failures documented as "resolusi versi TNC Template" in
	# docs/audit/ringkasan-seluruh-sprint.md), nothing ever re-creates it,
	# because the patch itself won't run a second time. The consequence is
	# silent, not an error: quotation_hooks._set_active_tnc_template just
	# finds no matching template and leaves doc.tnc_template unset on every
	# new Quotation from then on -- confirmed live, the merged Quotation PDF
	# button (quotation_print.py) quietly skips the whole T&C section with
	# no visible sign anything is wrong. Re-running each patch's own
	# (already idempotent) execute() every migrate closes that gap, same
	# self-healing pattern as _ensure_sai_branding above.
	from starlab_customizations.patches import seed_tnc_master_template, seed_tnc_master_template_v2

	seed_tnc_master_template.execute()
	seed_tnc_master_template_v2.execute()


def _restructure_selling_workspace():
	# 2026-08-24: same drift class as _ensure_tnc_master_templates above -- "Selling"
	# and "ERPNext Settings" are standard ERPNext Workspaces, reset by erpnext's own
	# module sync on `bench migrate` (same reasoning as
	# SYSTEM_MANAGER_ONLY_WORKSPACES/_restrict_admin_workspaces_to_system_manager
	# above, which is why "Selling" is already in that list -- restricting who can
	# see the Workspace icon doesn't stop erpnext's sync from resetting the
	# Workspace's own content/links every migrate). patches/
	# restructure_selling_and_org_menu.py already applied the menu cleanup once
	# ([post_model_sync], patches.txt) -- but a patch never re-runs, so a later
	# erpnext sync can silently undo it on a long-lived site (confirmed missing on
	# this project's own dev site). Re-run the patch's own (now idempotent, see
	# _selling_already_restructured guard in that file) execute() every migrate
	# instead of re-implementing the Workspace-editing logic a second time here --
	# same "call the existing patch's function" pattern as
	# _ensure_tnc_master_templates.
	from starlab_customizations.patches import restructure_selling_and_org_menu

	restructure_selling_and_org_menu.execute()


def after_migrate():
	_ensure_company()
	_ensure_fiscal_year()
	_ensure_indonesian_language()
	_ensure_setup_complete()
	_ensure_sai_branding()
	_ensure_tnc_master_templates()
	_restrict_admin_workspaces_to_system_manager()
	_rehide_unused_workspaces()
	_ensure_hr_workspace_sidebar()
	_ensure_crm_starlab_shortcuts()
	_restructure_selling_workspace()

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
