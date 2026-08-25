import frappe


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "No Dokumen", "fieldname": "document_no", "fieldtype": "Data", "width": 120},
		{"label": "Nama Dokumen", "fieldname": "document_name", "fieldtype": "Data", "width": 200},
		{"label": "Level", "fieldname": "document_level", "fieldtype": "Data", "width": 180},
		{"label": "Status Dokumen", "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": "Divisi", "fieldname": "divisi", "fieldtype": "Data", "width": 110},
		{"label": "Tanggal Distribusi", "fieldname": "tanggal_distribusi", "fieldtype": "Date", "width": 120},
		{"label": "Sudah Dibaca", "fieldname": "acknowledged", "fieldtype": "Check", "width": 90},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("document_level"):
		conditions.append("m.document_level = %(document_level)s")
		values["document_level"] = filters["document_level"]
	if filters.get("status"):
		conditions.append("m.status = %(status)s")
		values["status"] = filters["status"]
	if filters.get("divisi"):
		conditions.append("d.divisi = %(divisi)s")
		values["divisi"] = filters["divisi"]

	where_clause = " AND " + " AND ".join(conditions) if conditions else ""

	return frappe.db.sql(
		f"""
		SELECT
			m.document_no AS document_no,
			m.document_name AS document_name,
			m.document_level AS document_level,
			m.status AS status,
			d.divisi AS divisi,
			d.tanggal_distribusi AS tanggal_distribusi,
			d.acknowledged AS acknowledged
		FROM `tabDocument Master` m
		INNER JOIN `tabDocument Distribution` d ON d.parent = m.name
		WHERE 1=1 {where_clause}
		ORDER BY m.document_no, d.divisi
		LIMIT 5000
		""",
		values,
		as_dict=1,
	)
