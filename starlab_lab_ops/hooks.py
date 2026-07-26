app_name = "starlab_lab_ops"
app_title = "Starlab Lab Ops"
app_publisher = "Starlab"
app_description = "Modul operasional LIMS PT Starlab"
app_email = "alvirariskyy@gmail.com"
app_license = "mit"

# Send non-GET requests for this app's endpoints as native `application/json`
# bodies instead of form-encoded, per-key JSON-stringified values.
use_json_request_body = True

# Apps
# ------------------

# starlab_quality is required because Test Parameter.metode_uji is a Link
# field with options="Document Master" (owned by starlab_quality) baked
# directly into test_parameter.json. Installing/migrating this app before
# starlab_quality exists raises WrongOptionsDoctypeLinkError. Declaring it
# here makes `bench install-app starlab_lab_ops` auto-install starlab_quality
# first if it isn't already present.
required_apps = ["erpnext", "starlab_quality"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "starlab_lab_ops",
# 		"logo": "/assets/starlab_lab_ops/logo.png",
# 		"title": "Starlab Lab Ops",
# 		"route": "/starlab_lab_ops",
# 		"has_permission": "starlab_lab_ops.api.permission.has_app_permission",
# 	}
# ]

# Companion apps that extend a host app (instead of taking their own apps-screen icon) can pin
# their workspaces into the host app's workspace dock (rail) with this hook. Declaring it keeps
# the app off the apps screen, so it takes precedence over any add_to_apps_screen above. Who can
# see a pinned workspace is controlled by that workspace's own Roles table.
# add_to_workspace_dock = [
# 	{
# 		"app": "erpnext",
# 		"workspace": "My Workspace",
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/starlab_lab_ops/css/starlab_lab_ops.css"
# app_include_js = "/assets/starlab_lab_ops/js/starlab_lab_ops.js"

# include js, css files in header of web template
# web_include_css = "/assets/starlab_lab_ops/css/starlab_lab_ops.css"
# web_include_js = "/assets/starlab_lab_ops/js/starlab_lab_ops.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "starlab_lab_ops/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "starlab_lab_ops/public/icons.svg"

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
# 	"methods": "starlab_lab_ops.utils.jinja_methods",
# 	"filters": "starlab_lab_ops.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "starlab_lab_ops.install.before_install"
# after_install = "starlab_lab_ops.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "starlab_lab_ops.uninstall.before_uninstall"
# after_uninstall = "starlab_lab_ops.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "starlab_lab_ops.utils.before_app_install"
# after_app_install = "starlab_lab_ops.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "starlab_lab_ops.utils.before_app_uninstall"
# after_app_uninstall = "starlab_lab_ops.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "starlab_lab_ops.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "starlab_lab_ops.notifications.get_notification_config"

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
	"Work Order Pengujian": {
		"validate": "starlab_lab_ops.wo_hooks.validate_work_order",
		"on_update": "starlab_lab_ops.wo_hooks.on_update_work_order",
	},
	"Sample": {
		"validate": "starlab_lab_ops.wo_hooks.validate_sample",
	},
	"Test Result": {
		"validate": "starlab_lab_ops.wo_hooks.validate_test_result",
		"on_update": "starlab_lab_ops.wo_hooks.on_update_test_result",
	},
	"LHU": {
		"validate": "starlab_lab_ops.lhu_hooks.populate_test_result_list",
	},
}

# Fixtures
# --------
# Config records (not doctype source) that need to ship as part of this
# app's code so a fresh install recreates the Work Order Pengujian workflow.

fixtures = [
	{
		"dt": "Workflow State",
		"filters": [
			["name", "in", [
				"Draft", "In Progress", "Completed", "Diterima", "Sedang Diuji", "Divalidasi", "Diarsipkan",
				"Dimusnahkan", "Diajukan Validasi", "Ditolak",
			]]
		],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [
			["name", "in", [
				"Mulai Pengujian", "Selesaikan", "Buka Kembali", "Mulai Uji", "Arsipkan", "Musnahkan",
				"Ajukan Validasi", "Validasi", "Batalkan Validasi", "Tolak", "Revisi",
			]]
		],
	},
	{"dt": "Workflow", "filters": [["document_type", "in", ["Work Order Pengujian", "Sample", "Test Result"]]]},
	{"dt": "Custom Field", "filters": [["dt", "=", "Work Order Pengujian"]]},
	{
		"dt": "Custom DocPerm",
		"filters": [
			["parent", "in", ["Work Order Pengujian", "Sample", "Test Result", "LHU"]],
			["role", "in", ["Administrasi", "Manajer Teknis", "Laboratorium", "Direksi", "Marketing", "Finance", "Manajer Mutu"]],
		],
	},
	{
		"dt": "Number Card",
		"filters": [
			["name", "in", [
				"Sample Belum Diuji", "Sample Sedang Diuji", "WO Aktif", "WO Selesai",
				"WO Draft Menunggu Approval", "Test Result Menunggu Validasi", "Test Result Ditolak",
				"LHU Draft Menunggu Diterbitkan",
			]]
		],
	},
]

# Note: the "Starlab Lab Ops" Workspace itself is NOT a fixture here on purpose --
# it's private to the dev/test user tester@starlab.local, so exporting it would
# try to recreate a Workspace pointing at a user that may not exist on another
# install. The 2 Number Cards above are the actual portable Sprint 4 deliverable;
# which Workspace happens to display them is a per-environment convenience.

# Scheduled Tasks
# ---------------

# TSD Bagian 10 -- reminder deadline pengujian (H-2/terlewat) & retensi Sample.
scheduler_events = {
	"daily": [
		"starlab_lab_ops.tasks.check_sample_deadline_mendekat",
		"starlab_lab_ops.tasks.check_sample_deadline_terlewat",
		"starlab_lab_ops.tasks.check_sample_retensi",
	],
}

# Testing
# -------

# before_tests = "starlab_lab_ops.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "starlab_lab_ops.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "starlab_lab_ops.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "starlab_lab_ops.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["starlab_lab_ops.utils.before_request"]
# after_request = ["starlab_lab_ops.utils.after_request"]

# Job Events
# ----------
# before_job = ["starlab_lab_ops.utils.before_job"]
# after_job = ["starlab_lab_ops.utils.after_job"]

# after_file_upload = ["starlab_lab_ops.utils.after_file_upload"]

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
# 	"starlab_lab_ops.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# Require all whitelisted methods to have type annotations
require_type_annotated_api_methods = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

