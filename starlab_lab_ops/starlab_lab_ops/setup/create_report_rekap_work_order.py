import os

import frappe

REPORT_NAME = "Rekap Work Order"
MODULE = "Starlab Lab Ops"

PY_CONTENT = '''import frappe


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "Work Order", "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order Pengujian", "width": 150},
		{"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
		{"label": "Kegiatan", "fieldname": "kegiatan", "fieldtype": "Data", "width": 200},
		{"label": "Tanggal WO", "fieldname": "tanggal_wo", "fieldtype": "Date", "width": 100},
		{"label": "Status WO", "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": "Parameter", "fieldname": "parameter", "fieldtype": "Link", "options": "Test Parameter", "width": 200},
		{"label": "PJ Analis", "fieldname": "pj_analis", "fieldtype": "Link", "options": "Employee", "width": 140},
		{"label": "Target Pengujian", "fieldname": "target_pengujian", "fieldtype": "Date", "width": 110},
		{"label": "Status Pengujian", "fieldname": "status_pengujian", "fieldtype": "Data", "width": 110},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("from_date"):
		conditions.append("wo.tanggal_wo >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("wo.tanggal_wo <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("status"):
		conditions.append("wo.status = %(status)s")
		values["status"] = filters["status"]
	if filters.get("customer"):
		conditions.append("wo.customer = %(customer)s")
		values["customer"] = filters["customer"]
	if filters.get("pj_analis"):
		conditions.append("d.pj_analis = %(pj_analis)s")
		values["pj_analis"] = filters["pj_analis"]

	where_clause = " AND " + " AND ".join(conditions) if conditions else ""

	return frappe.db.sql(
		f"""
		SELECT
			wo.name AS work_order,
			wo.customer AS customer,
			wo.kegiatan AS kegiatan,
			wo.tanggal_wo AS tanggal_wo,
			wo.status AS status,
			d.parameter AS parameter,
			d.pj_analis AS pj_analis,
			d.target_pengujian AS target_pengujian,
			d.status_pengujian AS status_pengujian
		FROM `tabWork Order Pengujian` wo
		INNER JOIN `tabWO Parameter Detail` d ON d.parent = wo.name
		WHERE 1=1 {where_clause}
		ORDER BY wo.tanggal_wo DESC, wo.name
		""",
		values,
		as_dict=1,
	)
'''


def execute():
	if not frappe.db.exists("Report", REPORT_NAME):
		frappe.get_doc({
			"doctype": "Report",
			"report_name": REPORT_NAME,
			"ref_doctype": "Work Order Pengujian",
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
