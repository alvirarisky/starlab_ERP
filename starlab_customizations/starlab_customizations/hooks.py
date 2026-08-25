app_name = "starlab_customizations"
app_title = "Starlab Customizations"
app_publisher = "PT Starlab Analitik Indonesia"
app_description = "Customizations modul ERP SAI"
app_email = "banyugong3@gmail.com"
app_license = "mit"

# starlab_lab_ops is required because Client Inquiry Parameter Detail.parameter
# is a Link field with options="Test Parameter" (owned by starlab_lab_ops).
required_apps = ["starlab_lab_ops"]

# Includes in <head>
# ------------------

# Styling Papan Quotation & Papan Client Inquiry (page/quotation_board,
# page/client_inquiry_board) -- dimuat di semua halaman Desk lewat
# app_include_css (bukan cuma di 2 Page itu, karena Frappe tidak punya hook
# "load CSS ini cuma di Page X"), tapi semua class di file ini diberi prefix
# crm-kanban- jadi aman/tidak menimpa style Desk manapun di luar 2 Page itu.
app_include_css = "/assets/starlab_customizations/css/crm_kanban.css"

# Lihat komentar di public/js/redirect_to_role_workspace.js -- install.py's
# get_home_page cuma nyala sekali seusai submit form /login; kalau session
# masih aktif dan Desk dibuka langsung tanpa lewat login lagi, redirect itu
# tidak pernah kepanggil. Skrip ini menutup celah itu di app_ready.
app_include_js = "/assets/starlab_customizations/js/redirect_to_role_workspace.js"

# Aksen tombol brand SAI -- static CSS biasa, BUKAN lewat Website Theme
# custom_scss (lihat public/css/starlab_branding.css untuk kenapa; ringkas:
# Website Theme custom di versi Frappe ini kena bug kompilasi @import .css
# yang bikin ~25 asset 500 di setiap halaman website).
web_include_css = "/assets/starlab_customizations/css/starlab_branding.css"

# Lihat komentar di public/js/strip_generic_login_redirect.js -- perlu di
# SEMUA halaman website (bukan cuma /login) karena web_include_js dimuat
# lewat base template templates/web.html yang sama; script-nya sendiri
# early-return kalau bukan /login jadi aman/no-op di halaman lain.
web_include_js = "/assets/starlab_customizations/js/strip_generic_login_redirect.js"

doctype_js = {
	"Quotation": "public/js/quotation.js",
	"LHU": "public/js/lhu.js",
}

# Home Pages
# ----------

# Landing page per role begitu login -- tanpa ini, semua user (apa pun
# role-nya) mendarat di /desk generik, harus tahu dulu nama Workspace-nya
# sendiri buat pindah manual (masalah nyata buat user non-IT). Diarahkan ke
# Workspace ROLE spesifik masing-masing (bukan Workspace domain
# CRM/LIMS/Keuangan/Kualitas hasil nesting di Bagian 3.28), karena itu yang
# paling relevan buat kerja sehari-hari user itu -- domain overview tetap
# bisa diakses lewat expand Workspace picker.
#
# Pakai hook function (get_website_user_home_page), BUKAN dict
# role_home_page bawaan -- dict itu iterate frappe.get_roles() tanpa
# kontrol urutan, dan Administrator secara sintetis punya SEMUA role (lihat
# frappe.permissions.get_roles()), jadi bakal ke-redirect ke role PERTAMA
# yang match secara acak/tidak terduga alih-alih ke /desk generik seperti
# semestinya. install.get_home_page mengecualikan Administrator secara
# eksplisit.
get_website_user_home_page = "starlab_customizations.install.get_home_page"

after_migrate = "starlab_customizations.install.after_migrate"

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Quotation": {
		"autoname": "starlab_customizations.quotation_hooks.autoname",
		"onload": "starlab_customizations.quotation_hooks.onload",
		"validate": "starlab_customizations.quotation_hooks.validate",
		"on_update": "starlab_customizations.quotation_hooks.on_update",
		# Transisi "Aktifkan Kembali" (Kedaluwarsa -> Approved) terjadi
		# antara dua state yang sama-sama docstatus=1 -- Frappe memicu
		# on_update_after_submit untuk save seperti ini, BUKAN on_update
		# biasa (lihat _extend_expiry_on_reactivation di quotation_hooks.py).
		"on_update_after_submit": "starlab_customizations.quotation_hooks.on_update",
	},
	"Kaji Ulang Tender": {
		"on_update": "starlab_customizations.client_inquiry_hooks.sync_client_inquiry_from_kaji_ulang",
	},
	"Petty Cash Entry": {
		"on_update": "starlab_customizations.petty_cash_hooks.on_update_petty_cash_entry",
	},
	"Sales Invoice": {
		"validate": "starlab_customizations.invoice_hooks.set_due_date",
	},
}

# Fixtures
# --------
# Config records (not doctype/report source) that need to ship as part of
# this app's code so a fresh install recreates the Quotation approval flow.

fixtures = [
	{
		"dt": "Role",
		"filters": [
			[
				"name",
				"in",
				[
					"Direksi",
					"Manajer Teknis",
					"Manajer Mutu",
					"Finance",
					"Marketing",
					"Administrasi",
					"Laboratorium",
					"HR",
				],
			]
		],
	},
	{
		"dt": "Workflow State",
		"filters": [
			[
				"name",
				"in",
				[
					"Draft",
					"Menunggu Approval MT",
					"Menunggu Approval MM",
					"Menunggu Approval Direksi",
					"Approved",
					"Rejected",
					"Kedaluwarsa",
					"Cancelled",
					"Diajukan Kaji Ulang",
					"Disetujui MT",
					"Ditolak MT",
					"Menunggu Approval",
					"Disetujui",
				],
			]
		],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [["name", "in", ["Ajukan", "Setujui", "Tolak", "Revisi", "Batalkan", "Aktifkan Kembali"]]],
	},
	{
		"dt": "Workflow",
		"filters": [["document_type", "in", ["Quotation", "Client Inquiry", "Petty Cash Entry"]]],
	},
	{
		"dt": "Custom Field",
		"filters": [["dt", "in", ["Quotation", "Customer", "Print Settings", "Sales Invoice"]]],
	},
	{
		"dt": "Custom DocPerm",
		"filters": [
			[
				"parent",
				"in",
				[
					"Quotation",
					"Customer",
					"Client Inquiry",
					"Kaji Ulang Tender",
					"TNC Master Template",
					"Petty Cash Entry",
					"Sales Invoice",
					"Bank Account",
					"Bank Transaction",
					"Bank Reconciliation Tool",
					"Bank Statement Import",
					# 2026-08-14: 5 celah izin Read yang dilaporkan tester (OVERVIEW_PROJECT.md
					# Bagian 5 poin 5) -- role sudah punya akses ke suatu fitur, tapi fitur itu
					# diam-diam butuh baca DocType lain yang belum diizinkan.
					"Account",
					"Company",
					"Email Account",
					"Lead",
					# 2026-08-14: Item -- ref_doctype laporan "Rekap Stok Reagen dan
					# Consumable" di Workspace LIMS. Report.roles sudah benar mendaftarkan
					# Laboratorium/Manajer Teknis/Direksi, tapi Frappe JUGA mensyaratkan
					# permission langsung ke ref_doctype-nya (Item) di luar Report.roles --
					# tanpa itu laporannya ikut hilang dari sidebar sama seperti Test
					# Parameter di atas (starlab_lab_ops/hooks.py).
					"Item",
					# 2026-08-15: ditemukan lewat Papan Quotation -- Manajer Teknis/Manajer
					# Mutu/Direksi/Administrasi (4 role approver Quotation) semuanya tidak
					# punya read ke Account, padahal apply_workflow() -> doc.save() ->
					# validasi inti ERPNext (get_party_account_currency) diam-diam butuh
					# baca Account default Customer buat resolve currency, di SETIAP
					# transisi approval -- bukan cuma lewat papan baru ini, tombol Workflow
					# standar di Desk kena masalah yang sama. "Account" sendiri sudah ada
					# di daftar parent di atas (baris utk Finance) -- 4 role ini nyusul.
				],
			],
			[
				"role",
				"in",
				[
					"Direksi",
					"Manajer Teknis",
					"Manajer Mutu",
					"Finance",
					"Marketing",
					"Administrasi",
					# Laboratorium ditambahkan bareng "Customer" jadi baris ke-2 poin di atas --
					# Laboratorium sengaja tidak pernah masuk daftar role di sini sebelumnya.
					"Laboratorium",
				],
			],
		],
	},
	{
		# Page (core Frappe DocType, dipakai internal buat resolusi route Desk)
		# defaultnya cuma bisa dibaca Administrator/System Manager -- role
		# custom manapun di project ini (Direksi, Marketing, Laboratorium,
		# dst) jadi kena 403 "No permission for Page" begitu SPA Desk coba
		# resolve route Workspace apapun (termasuk 7 Workspace role lama,
		# bukan cuma CRM/LIMS), bikin seluruh render Desk gagal buat mereka.
		# Fix: read-only ke role "All" (built-in, otomatis dipegang semua
		# user) -- bukan doctype data bisnis, aman dibuka lebar buat semua
		# user internal yang login.
		"dt": "Custom DocPerm",
		"filters": [
			["parent", "=", "Page"],
			["role", "=", "All"],
		],
	},
	{
		# User doctype defaultnya cuma "read" ke System Manager di instance ini
		# (bukan default Frappe/ERPNext standar) -- hampir semua data seed
		# dimiliki (owner) "Administrator", jadi widget apapun yang coba
		# resolve identitas user LAIN (Assign To, "Dibuat oleh"/"Diubah oleh"
		# di timeline & list view, dst.) kena 403 "No permission for User"
		# untuk role custom manapun begitu mereka lihat dokumen bukan
		# buatannya sendiri -- baca profil sendiri tetap selalu boleh (Frappe
		# core punya exception bawaan untuk itu), yang gak boleh cuma profil
		# ORANG LAIN. Fix: read-only ke role "All", persis default Frappe
		# stock -- field sensitif (API key dkk) tetap terkunci System
		# Manager karena ada di permlevel 1 terpisah, tidak tersentuh baris
		# ini (permlevel 0).
		"dt": "Custom DocPerm",
		"filters": [
			["parent", "=", "User"],
			["role", "=", "All"],
		],
	},
	{
		# Role "HR" -- akses ke DocType modul HR/Payroll bawaan app `hrms`
		# (github.com/frappe/hrms, required_apps erpnext), BUKAN DocType custom
		# project ini sendiri. Dipisah dari entry Custom DocPerm business-doctype
		# di atas (yang isinya DocType starlab_customizations) supaya gak
		# nyampur dua kategori DocType yang beda sumbernya. Payroll sengaja
		# cuma akses menu/CRUD DocType -- TIDAK ada Salary Structure/pemetaan
		# akun GL (butuh Chart of Account riil dari Finance dulu, sama seperti
		# kasus akun "Beban Operasional Kantor" placeholder di Petty Cash).
		# Approval pakai mekanisme bawaan hrms (Leave Application.leave_approver,
		# Payroll Entry submit/cancel biasa) -- bukan Frappe Workflow custom.
		"dt": "Custom DocPerm",
		"filters": [
			[
				"parent",
				"in",
				[
					"Employee",
					"Attendance",
					"Leave Application",
					"Leave Type",
					"Leave Allocation",
					"Payroll Entry",
					"Salary Slip",
					"Salary Structure",
					"Salary Structure Assignment",
					"Salary Component",
					"Training Event",
					"Training Program",
					"Training Result",
					"Training Feedback",
					"Appraisal",
					"Appraisal Template",
					"Goal",
				],
			],
			["role", "=", "HR"],
		],
	},
	{
		"dt": "Number Card",
		"filters": [
			[
				"name",
				"in",
				[
					"Quotation Draft",
					"Quotation Approved",
					"Quotation Rejected",
					"Quotation Menunggu Approval Direksi",
					"Petty Cash Menunggu Approval",
					"Petty Cash Disetujui Bulan Ini",
					"Invoice Overdue",
					"Invoice Unpaid",
					"Invoice Due 7 Hari",
					"Client Inquiry Draft",
					"Client Inquiry Diajukan Kaji Ulang",
					"Client Inquiry Disetujui MT",
					"Client Inquiry Ditolak MT",
				],
			]
		],
	},
	{
		"dt": "Dashboard",
		"filters": [
			[
				"name",
				"in",
				[
					"Dashboard Direksi",
					"Dashboard Marketing",
					"Dashboard Administrasi",
					"Dashboard Finance",
					"Dashboard Laboratorium",
					"Dashboard Manajer Teknis",
					"Dashboard Manajer Mutu",
				],
			]
		],
	},
	{
		"dt": "Dashboard Chart",
		"filters": [
			[
				"name",
				"in",
				[
					"Tren Quotation Dibuat",
					"Tren Invoice Dibuat",
					"Tren Sample Diterima",
					"Tren Test Result Dibuat",
					"Tren Dokumen Direvisi",
					"Funnel Form A - Quotation - Approved",
				],
			]
		],
	},
]

# Workspace TIDAK lewat mekanisme fixtures di atas -- Frappe mensinkronkan
# Workspace sebagai "module doc" biasa (seperti DocType/Report), dibaca
# langsung dari starlab_customizations/starlab_customizations/workspace/
# <slug>/<slug>.json saat bench migrate. Kalau didaftarkan di fixtures,
# migrate malah MENGHAPUSNYA di langkah "Removing orphan Workspaces" karena
# tidak ketemu file module yang cocok.

# Scheduled Tasks
# ---------------

# PRD v6 SS5.5 -- eskalasi SLA approval Quotation (>1x24 jam) & notifikasi
# auto-expiry. Lihat starlab_customizations/tasks.py untuk detail + TODO
# terkait Open Question #1 (target eskalasi belum dikonfirmasi PO).
scheduler_events = {
	"hourly": [
		"starlab_customizations.tasks.check_quotation_sla",
	],
	"daily": [
		"starlab_customizations.tasks.check_quotation_expiry",
		"starlab_customizations.tasks.check_invoice_due",
		"starlab_customizations.tasks.check_invoice_overdue",
	],
}
