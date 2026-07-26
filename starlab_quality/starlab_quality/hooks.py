app_name = "starlab_quality"
app_title = "Starlab Quality"
app_publisher = "PT Starlab Analitik Indonesia"
app_description = "Modul manajemen mutu ISO 17025 SAI"
app_email = "banyugong3@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "starlab_quality",
# 		"logo": "/assets/starlab_quality/logo.png",
# 		"title": "Starlab Quality",
# 		"route": "/starlab_quality",
# 		"has_permission": "starlab_quality.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/starlab_quality/css/starlab_quality.css"
# app_include_js = "/assets/starlab_quality/js/starlab_quality.js"

# include js, css files in header of web template
# web_include_css = "/assets/starlab_quality/css/starlab_quality.css"
# web_include_js = "/assets/starlab_quality/js/starlab_quality.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "starlab_quality/public/scss/website"

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
# app_include_icons = "starlab_quality/public/icons.svg"

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
# 	"methods": "starlab_quality.utils.jinja_methods",
# 	"filters": "starlab_quality.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "starlab_quality.install.before_install"
# after_install = "starlab_quality.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "starlab_quality.uninstall.before_uninstall"
# after_uninstall = "starlab_quality.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "starlab_quality.utils.before_app_install"
# after_app_install = "starlab_quality.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "starlab_quality.utils.before_app_uninstall"
# after_app_uninstall = "starlab_quality.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "starlab_quality.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "starlab_quality.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# TSD SS7.8: sebagian besar role hanya boleh melihat Document Master yang
# "didistribusikan ke divisinya" -- row-level restriction, bukan
# doctype-level, jadi tidak cukup dengan Custom DocPerm biasa.
permission_query_conditions = {
	"Document Master": "starlab_quality.document_control_hooks.get_permission_query_conditions",
}

has_permission = {
	"Document Master": "starlab_quality.document_control_hooks.has_permission",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Document Master": {
		"validate": "starlab_quality.document_control_hooks.validate_document_master",
		"on_update": "starlab_quality.document_control_hooks.on_update_document_master",
	},
}

# Fixtures
# --------
# Config records (not doctype source) that need to ship as part of this
# app's code so a fresh install recreates the Document Control workflow.

fixtures = [
	{
		"dt": "Workflow State",
		"filters": [
			["name", "in", ["Draft", "Menunggu Approval MM", "Menunggu Approval Direksi", "Aktif", "Dalam Revisi"]]
		],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [["name", "in", ["Ajukan", "Setujui", "Tolak", "Terbitkan", "Mulai Revisi"]]],
	},
	{"dt": "Workflow", "filters": [["document_type", "=", "Document Master"]]},
	{
		"dt": "Custom DocPerm",
		"filters": [
			["parent", "=", "Document Master"],
			["role", "in", [
				"Direksi", "Manajer Teknis", "Manajer Mutu", "Finance", "Marketing", "Administrasi", "Laboratorium",
			]],
		],
	},
]

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"starlab_quality.tasks.all"
# 	],
# 	"daily": [
# 		"starlab_quality.tasks.daily"
# 	],
# 	"hourly": [
# 		"starlab_quality.tasks.hourly"
# 	],
# 	"weekly": [
# 		"starlab_quality.tasks.weekly"
# 	],
# 	"monthly": [
# 		"starlab_quality.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "starlab_quality.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "starlab_quality.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "starlab_quality.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "starlab_quality.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["starlab_quality.utils.before_request"]
# after_request = ["starlab_quality.utils.after_request"]

# Job Events
# ----------
# before_job = ["starlab_quality.utils.before_job"]
# after_job = ["starlab_quality.utils.after_job"]

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
# 	"starlab_quality.auth.validate"
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

