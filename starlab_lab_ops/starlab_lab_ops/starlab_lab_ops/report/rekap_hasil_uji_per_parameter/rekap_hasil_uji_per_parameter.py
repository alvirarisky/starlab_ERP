import frappe


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{
			"label": "Test Result",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Test Result",
			"width": 130,
		},
		{
			"label": "Parameter",
			"fieldname": "parameter",
			"fieldtype": "Link",
			"options": "Test Parameter",
			"width": 200,
		},
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
		LIMIT 5000
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
