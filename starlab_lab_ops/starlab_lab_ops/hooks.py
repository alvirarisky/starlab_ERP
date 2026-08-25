app_name = "starlab_lab_ops"
app_title = "Starlab Lab Ops"
app_publisher = "Starlab"
app_description = "Modul operasional LIMS PT Starlab"
app_email = "alvirariskyy@gmail.com"
app_license = "mit"

# Send non-GET requests for this app's endpoints as native `application/json`
# bodies instead of form-encoded, per-key JSON-stringified values.
use_json_request_body = True

# starlab_quality is required because Test Parameter.metode_uji is a Link
# field with options="Document Master" (owned by starlab_quality) baked
# directly into test_parameter.json. Installing/migrating this app before
# starlab_quality exists raises WrongOptionsDoctypeLinkError. Declaring it
# here makes `bench install-app starlab_lab_ops` auto-install starlab_quality
# first if it isn't already present.
required_apps = ["erpnext", "starlab_quality"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# Client Portal (starlab_integrations) memberi role Customer akses "read"
# doctype-level ke LHU (lihat lhu.json permissions) supaya /status-klien
# tidak PermissionError -- hook di bawah menutup row-level, supaya Customer
# cuma bisa baca LHU milik company-nya sendiri, bukan LHU company lain.
permission_query_conditions = {
	"LHU": "starlab_lab_ops.lhu_hooks.get_permission_query_conditions",
}

has_permission = {
	"LHU": "starlab_lab_ops.lhu_hooks.has_permission",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Work Order Pengujian": {
		"validate": "starlab_lab_ops.wo_hooks.validate_work_order",
		"on_update": [
			"starlab_lab_ops.wo_hooks.on_update_work_order",
			"starlab_lab_ops.wo_hooks.handle_subkon_flagging",
		],
	},
	"WO Eksternal": {
		"validate": "starlab_lab_ops.wo_eksternal_hooks.validate_wo_eksternal",
		"on_update": "starlab_lab_ops.wo_eksternal_hooks.on_update_wo_eksternal",
	},
	"Sample": {
		"validate": "starlab_lab_ops.wo_hooks.validate_sample",
		"on_update": "starlab_lab_ops.wo_hooks.on_update_sample",
	},
	"Test Result": {
		"validate": "starlab_lab_ops.wo_hooks.validate_test_result",
		"on_update": "starlab_lab_ops.wo_hooks.on_update_test_result",
	},
	"LHU": {
		"validate": "starlab_lab_ops.lhu_hooks.populate_test_result_list",
		"before_insert": "starlab_lab_ops.lhu_hooks.before_insert",
		"on_submit": "starlab_lab_ops.lhu_hooks.on_submit",
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
			[
				"name",
				"in",
				[
					"Draft",
					"In Progress",
					"Completed",
					"Diterima",
					"Sedang Diuji",
					"Divalidasi",
					"Diarsipkan",
					"Dimusnahkan",
					"Diajukan Validasi",
					"Ditolak",
				],
			]
		],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [
			[
				"name",
				"in",
				[
					"Mulai Pengujian",
					"Selesaikan",
					"Buka Kembali",
					"Mulai Uji",
					"Arsipkan",
					"Musnahkan",
					"Ajukan Validasi",
					"Validasi",
					"Batalkan Validasi",
					"Tolak",
					"Revisi",
				],
			]
		],
	},
	{
		"dt": "Workflow",
		"filters": [
			["document_type", "in", ["Work Order Pengujian", "Sample", "Test Result", "WO Eksternal"]]
		],
	},
	{"dt": "Custom Field", "filters": [["dt", "=", "Work Order Pengujian"]]},
	{
		"dt": "Custom DocPerm",
		"filters": [
			[
				"parent",
				"in",
				[
					"Work Order Pengujian",
					"Sample",
					"Test Result",
					"LHU",
					"WO Eksternal",
					# 2026-08-14: Test Parameter cuma punya permission "System Manager"
					# sejak dibuat -- shortcut "Test Parameter" di Workspace LIMS diam-diam
					# hilang dari sidebar Laboratorium/Manajer Teknis/Direksi (Frappe
					# menyembunyikan shortcut Workspace kalau role-nya tidak punya read,
					# tanpa pesan error apa pun -- makanya kelihatan seperti "belum
					# dikasih akses" padahal sebenarnya memang belum pernah diizinkan).
					"Test Parameter",
				],
			],
			[
				"role",
				"in",
				[
					"Administrasi",
					"Manajer Teknis",
					"Laboratorium",
					"Direksi",
					"Marketing",
					"Finance",
					"Manajer Mutu",
					"Customer",
				],
			],
		],
	},
	{
		"dt": "Number Card",
		"filters": [
			[
				"name",
				"in",
				[
					"Sample Belum Diuji",
					"Sample Sedang Diuji",
					"WO Aktif",
					"WO Selesai",
					"WO Draft Menunggu Approval",
					"Test Result Menunggu Validasi",
					"Test Result Ditolak",
					"LHU Draft Menunggu Diterbitkan",
				],
			]
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

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# Require all whitelisted methods to have type annotations
require_type_annotated_api_methods = True
