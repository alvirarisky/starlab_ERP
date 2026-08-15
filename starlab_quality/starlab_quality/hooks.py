app_name = "starlab_quality"
app_title = "Starlab Quality"
app_publisher = "PT Starlab Analitik Indonesia"
app_description = "Modul manajemen mutu ISO 17025 SAI"
app_email = "banyugong3@gmail.com"
app_license = "mit"

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
			[
				"name",
				"in",
				["Draft", "Menunggu Approval MM", "Menunggu Approval Direksi", "Aktif", "Dalam Revisi"],
			]
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
					"Laboratorium",
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
					"Dokumen Menunggu Approval MM",
					"Dokumen Menunggu Approval Direksi",
					"Dokumen Aktif",
					"Dokumen Usang",
					"Distribusi Belum Dibaca",
				],
			]
		],
	},
]
