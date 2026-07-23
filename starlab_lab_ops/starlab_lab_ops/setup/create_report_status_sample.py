import os

import frappe

REPORT_NAME = "Status Sample Realtime"
MODULE = "Starlab Lab Ops"

QUERY = """
SELECT
	name as "Sample:Link/Sample:120",
	work_order as "Work Order:Link/Work Order Pengujian:150",
	matriks as "Matriks::120",
	tanggal_terima as "Tanggal Terima:Date:110",
	status as "Status::110",
	retensi as "Retensi::100",
	tanggal_musnah as "Tanggal Musnah:Date:110"
FROM `tabSample`
WHERE
	(%(status)s = '' OR status = %(status)s)
	AND (%(matriks)s = '' OR matriks = %(matriks)s)
	AND (%(work_order)s = '' OR work_order = %(work_order)s)
ORDER BY tanggal_terima DESC
"""

JS_CONTENT = '''frappe.query_reports["Status Sample Realtime"] = {
	"filters": [
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\\nDiterima\\nSedang Diuji\\nDivalidasi\\nDiarsipkan\\nDimusnahkan",
			"default": "",
		},
		{
			"fieldname": "matriks",
			"label": __("Matriks"),
			"fieldtype": "Select",
			"options": "\\nUdara Ambien\\nUdara Emisi\\nAir Permukaan\\nAir Bersih\\nAir Limbah\\nTanah\\nSedimen\\nKebisingan",
			"default": "",
		},
		{
			"fieldname": "work_order",
			"label": __("Work Order"),
			"fieldtype": "Link",
			"options": "Work Order Pengujian",
			"default": "",
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "status") {
			const colors = {
				"Diterima": "blue",
				"Sedang Diuji": "orange",
				"Divalidasi": "green",
				"Diarsipkan": "gray",
				"Dimusnahkan": "red",
			};
			const color = colors[data.status] || "gray";
			value = `<span class="indicator-pill ${color}">${data.status}</span>`;
		}
		return value;
	},
};
'''


def execute():
	if not frappe.db.exists("Report", REPORT_NAME):
		frappe.get_doc({
			"doctype": "Report",
			"report_name": REPORT_NAME,
			"ref_doctype": "Sample",
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

	app_path = frappe.get_app_path("starlab_lab_ops")
	report_dir = os.path.join(app_path, "starlab_lab_ops", "report", frappe.scrub(REPORT_NAME))
	js_file = os.path.join(report_dir, frappe.scrub(REPORT_NAME) + ".js")
	os.makedirs(report_dir, exist_ok=True)
	with open(js_file, "w") as f:
		f.write(JS_CONTENT)
	print(f"Wrote report client script to {js_file}")
