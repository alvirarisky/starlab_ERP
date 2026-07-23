import frappe

REPORT_NAME = "Rekap Kepatuhan Dokumen Mutu"
MODULE = "Starlab Quality"

QUERY = """
SELECT
	m.document_no as "No Dokumen:Data:120",
	m.document_name as "Nama Dokumen:Data:200",
	m.document_level as "Level::180",
	m.status as "Status Dokumen::100",
	d.divisi as "Divisi::110",
	d.tanggal_distribusi as "Tanggal Distribusi:Date:120",
	d.acknowledged as "Acknowledged:Check:90"
FROM `tabDocument Master` m
INNER JOIN `tabDocument Distribution` d ON d.parent = m.name
WHERE
	(%(document_level)s = '' OR m.document_level = %(document_level)s)
	AND (%(status)s = '' OR m.status = %(status)s)
	AND (%(divisi)s = '' OR d.divisi = %(divisi)s)
ORDER BY m.document_no, d.divisi
"""

JS_CONTENT = '''frappe.query_reports["Rekap Kepatuhan Dokumen Mutu"] = {
	"filters": [
		{
			"fieldname": "document_level",
			"label": __("Level Dokumen"),
			"fieldtype": "Select",
			"options": "\\nPM - Panduan Mutu\\nPO - Prosedur Operasional\\nIKM - Instruksi Kerja Metode\\nDP - Dokumen Pendukung",
			"default": "",
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\\nAktif\\nDalam Revisi\\nUsang",
			"default": "",
		},
		{
			"fieldname": "divisi",
			"label": __("Divisi"),
			"fieldtype": "Select",
			"options": "\\nDireksi\\nMM\\nMT\\nLaboratorium\\nAdministrasi\\nFinance\\nMarketing",
			"default": "",
		},
	],
};
'''


def execute():
	if not frappe.db.exists("Report", REPORT_NAME):
		frappe.get_doc({
			"doctype": "Report",
			"report_name": REPORT_NAME,
			"ref_doctype": "Document Master",
			"report_type": "Query Report",
			"module": MODULE,
			"is_standard": "Yes",
			"query": QUERY,
			"roles": [{"role": "System Manager"}],
		}).insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"Report '{REPORT_NAME}' created.")
	else:
		doc = frappe.get_doc("Report", REPORT_NAME)
		doc.query = QUERY
		doc.save(ignore_permissions=True)
		frappe.db.commit()
		print(f"Report '{REPORT_NAME}' already exists, query updated.")

	import os
	app_path = frappe.get_app_path("starlab_quality")
	report_dir = os.path.join(app_path, "starlab_quality", "report", frappe.scrub(REPORT_NAME))
	js_file = os.path.join(report_dir, frappe.scrub(REPORT_NAME) + ".js")
	os.makedirs(report_dir, exist_ok=True)
	with open(js_file, "w") as f:
		f.write(JS_CONTENT)
	print(f"Wrote report client script to {js_file}")
