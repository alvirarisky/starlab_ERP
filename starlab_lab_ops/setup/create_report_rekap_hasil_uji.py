import os

import frappe

REPORT_NAME = "Rekap Hasil Uji per Parameter"
MODULE = "Starlab Lab Ops"

PY_CONTENT = '''import frappe


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": "Test Result", "fieldname": "name", "fieldtype": "Link", "options": "Test Result", "width": 130},
		{"label": "Parameter", "fieldname": "parameter", "fieldtype": "Link", "options": "Test Parameter", "width": 200},
		{"label": "Analis", "fieldname": "analis", "fieldtype": "Link", "options": "Employee", "width": 130},
		{"label": "Hasil Uji", "fieldname": "hasil_uji", "fieldtype": "Float", "width": 100},
		{"label": "Satuan", "fieldname": "satuan", "fieldtype": "Data", "width": 90},
		{"label": "Status Validasi", "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": "Tanggal Dibuat", "fieldname": "creation", "fieldtype": "Datetime", "width": 150},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("parameter"):
		conditions.append("parameter = %(parameter)s")
		values["parameter"] = filters["parameter"]
	if filters.get("analis"):
		conditions.append("analis = %(analis)s")
		values["analis"] = filters["analis"]
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]
	if filters.get("from_date"):
		conditions.append("DATE(creation) >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("DATE(creation) <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	where_clause = " AND " + " AND ".join(conditions) if conditions else ""

	return frappe.db.sql(
		f"""
		SELECT name, parameter, analis, hasil_uji, satuan, status, creation
		FROM `tabTest Result`
		WHERE 1=1 {where_clause}
		ORDER BY creation DESC
		""",
		values,
		as_dict=1,
	)


def get_chart(data):
	counts = {}
	for row in data:
		counts[row["parameter"]] = counts.get(row["parameter"], 0) + 1
	labels = list(counts.keys())
	values = [counts[k] for k in labels]
	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": "Jumlah Hasil Uji", "values": values}],
		},
		"type": "bar",
	}
'''


def execute():
	if not frappe.db.exists("Report", REPORT_NAME):
		frappe.get_doc({
			"doctype": "Report",
			"report_name": REPORT_NAME,
			"ref_doctype": "Test Result",
			"report_type": "Script Report",
			"module": MODULE,
			"is_standard": "Yes",
			"roles": [{"role": "System Manager"}],
		}).insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"Report '{REPORT_NAME}' created.")
	else:
		print(f"Report '{REPORT_NAME}' already exists.")

	app_path = frappe.get_app_path("starlab_lab_ops")
	report_dir = os.path.join(app_path, "starlab_lab_ops", "report", frappe.scrub(REPORT_NAME))
	py_file = os.path.join(report_dir, frappe.scrub(REPORT_NAME) + ".py")
	os.makedirs(report_dir, exist_ok=True)
	with open(py_file, "w") as f:
		f.write(PY_CONTENT)
	print(f"Wrote report logic to {py_file}")
