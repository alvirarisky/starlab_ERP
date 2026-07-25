import frappe


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": "Work Order", "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order Pengujian", "width": 130},
		{"label": "Matriks", "fieldname": "matriks", "fieldtype": "Data", "width": 110},
		{"label": "Parameter", "fieldname": "parameter", "fieldtype": "Link", "options": "Test Parameter", "width": 200},
		{"label": "PJ Analis", "fieldname": "pj_analis", "fieldtype": "Link", "options": "Employee", "width": 120},
		{"label": "Target Pengujian", "fieldname": "target_pengujian", "fieldtype": "Date", "width": 110},
		{"label": "Tanggal Selesai Aktual", "fieldname": "tanggal_selesai_aktual", "fieldtype": "Date", "width": 130},
		{"label": "Status SLA", "fieldname": "status_sla", "fieldtype": "Data", "width": 110},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("matriks"):
		conditions.append("d.matriks = %(matriks)s")
		values["matriks"] = filters["matriks"]
	if filters.get("from_date"):
		conditions.append("d.target_pengujian >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("d.target_pengujian <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	where_clause = " AND " + " AND ".join(conditions) if conditions else ""

	rows = frappe.db.sql(
		f"""
		SELECT
			d.parent AS work_order,
			d.matriks AS matriks,
			d.parameter AS parameter,
			d.pj_analis AS pj_analis,
			d.target_pengujian AS target_pengujian
		FROM `tabWO Parameter Detail` d
		WHERE 1=1 {where_clause}
		ORDER BY d.target_pengujian DESC
		""",
		values,
		as_dict=1,
	)

	result = []
	for row in rows:
		actual = frappe.db.sql(
			"""
			SELECT MIN(tr.creation) AS selesai
			FROM `tabTest Result` tr
			WHERE tr.work_order = %(work_order)s AND tr.parameter = %(parameter)s
			""",
			{"work_order": row["work_order"], "parameter": row["parameter"]},
			as_dict=1,
		)
		selesai = actual[0]["selesai"] if actual else None
		tanggal_selesai_aktual = selesai.date() if selesai else None

		if not tanggal_selesai_aktual:
			status_sla = "Belum Selesai"
		elif tanggal_selesai_aktual > row["target_pengujian"]:
			status_sla = "Terlambat"
		else:
			status_sla = "Tepat Waktu"

		row["tanggal_selesai_aktual"] = tanggal_selesai_aktual
		row["status_sla"] = status_sla
		result.append(row)

	return result


def get_chart(data):
	summary = {}
	for row in data:
		matriks = row["matriks"]
		summary.setdefault(matriks, {"total": 0, "terlambat": 0})
		summary[matriks]["total"] += 1
		if row["status_sla"] == "Terlambat":
			summary[matriks]["terlambat"] += 1

	labels = list(summary.keys())
	values = [
		round(summary[m]["terlambat"] / summary[m]["total"] * 100, 1) if summary[m]["total"] else 0
		for m in labels
	]
	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": "% Keterlambatan", "values": values}],
		},
		"type": "bar",
	}
