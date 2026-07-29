app_name = "starlab_customizations"
app_title = "Starlab Customizations"
app_publisher = "PT Starlab Analitik Indonesia"
app_description = "Customizations modul ERP SAI"
app_email = "banyugong3@gmail.com"
app_license = "mit"

# Apps
# ------------------

# starlab_lab_ops is required because Client Inquiry Parameter Detail.parameter
# is a Link field with options="Test Parameter" (owned by starlab_lab_ops).
required_apps = ["starlab_lab_ops"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "starlab_customizations",
# 		"logo": "/assets/starlab_customizations/logo.png",
# 		"title": "Starlab Customizations",
# 		"route": "/starlab_customizations",
# 		"has_permission": "starlab_customizations.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/starlab_customizations/css/starlab_customizations.css"
# app_include_js = "/assets/starlab_customizations/js/starlab_customizations.js"

# include js, css files in header of web template
# web_include_css = "/assets/starlab_customizations/css/starlab_customizations.css"
# web_include_js = "/assets/starlab_customizations/js/starlab_customizations.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "starlab_customizations/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Quotation": "public/js/quotation.js",
	"LHU": "public/js/lhu.js",
}
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "starlab_customizations/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "starlab_customizations.utils.jinja_methods",
# 	"filters": "starlab_customizations.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "starlab_customizations.install.before_install"
# after_install = "starlab_customizations.install.after_install"

after_migrate = "starlab_customizations.install.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "starlab_customizations.uninstall.before_uninstall"
# after_uninstall = "starlab_customizations.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "starlab_customizations.utils.before_app_install"
# after_app_install = "starlab_customizations.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "starlab_customizations.utils.before_app_uninstall"
# after_app_uninstall = "starlab_customizations.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "starlab_customizations.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "starlab_customizations.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

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
			["name", "in", ["Direksi", "Manajer Teknis", "Manajer Mutu", "Finance", "Marketing", "Administrasi", "Laboratorium"]]
		],
	},
	{
		"dt": "Workflow State",
		"filters": [
			["name", "in", [
				"Draft", "Menunggu Approval MT", "Menunggu Approval MM",
				"Menunggu Approval Direksi", "Approved", "Rejected", "Kedaluwarsa", "Cancelled",
				"Diajukan Kaji Ulang", "Disetujui MT", "Ditolak MT", "Menunggu Approval", "Disetujui",
			]]
		],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [["name", "in", ["Ajukan", "Setujui", "Tolak", "Revisi", "Batalkan"]]],
	},
	{"dt": "Workflow", "filters": [["document_type", "in", ["Quotation", "Client Inquiry", "Petty Cash Entry"]]]},
	{"dt": "Custom Field", "filters": [["dt", "in", ["Quotation", "Customer", "Print Settings", "Sales Invoice"]]]},
	{
		"dt": "Custom DocPerm",
		"filters": [
			["parent", "in", [
				"Quotation", "Customer", "Client Inquiry", "Kaji Ulang Tender", "TNC Master Template",
				"Petty Cash Entry", "Sales Invoice", "Bank Account", "Bank Transaction",
				"Bank Reconciliation Tool", "Bank Statement Import",
			]],
			["role", "in", ["Direksi", "Manajer Teknis", "Manajer Mutu", "Finance", "Marketing", "Administrasi"]],
		],
	},
	{
		"dt": "Number Card",
		"filters": [
			["name", "in", [
				"Quotation Draft", "Quotation Approved", "Quotation Rejected",
				"Quotation Menunggu Approval Direksi", "Petty Cash Menunggu Approval",
				"Petty Cash Disetujui Bulan Ini", "Invoice Overdue", "Invoice Unpaid", "Invoice Due 7 Hari",
				"Client Inquiry Draft", "Client Inquiry Diajukan Kaji Ulang",
				"Client Inquiry Disetujui MT", "Client Inquiry Ditolak MT",
			]]
		],
	},
	{
		"dt": "Dashboard",
		"filters": [
			["name", "in", [
				"Dashboard Direksi", "Dashboard Marketing", "Dashboard Administrasi", "Dashboard Finance",
				"Dashboard Laboratorium", "Dashboard Manajer Teknis", "Dashboard Manajer Mutu",
			]]
		],
	},
	{
		"dt": "Dashboard Chart",
		"filters": [
			["name", "in", [
				"Tren Quotation Dibuat", "Tren Invoice Dibuat", "Tren Sample Diterima",
				"Tren Test Result Dibuat", "Tren Dokumen Direvisi",
				"Funnel Form A - Quotation - Approved",
			]]
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

# Testing
# -------

# before_tests = "starlab_customizations.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "starlab_customizations.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "starlab_customizations.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "starlab_customizations.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["starlab_customizations.utils.before_request"]
# after_request = ["starlab_customizations.utils.after_request"]

# Job Events
# ----------
# before_job = ["starlab_customizations.utils.before_job"]
# after_job = ["starlab_customizations.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"starlab_customizations.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

