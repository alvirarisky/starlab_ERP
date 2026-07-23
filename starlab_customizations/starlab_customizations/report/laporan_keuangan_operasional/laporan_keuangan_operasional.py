import frappe


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "Tanggal", "fieldname": "tanggal", "fieldtype": "Date", "width": 100},
		{"label": "Kategori", "fieldname": "kategori", "fieldtype": "Data", "width": 120},
		{"label": "Referensi", "fieldname": "referensi", "fieldtype": "Data", "width": 150},
		{"label": "Keterangan", "fieldname": "keterangan", "fieldtype": "Data", "width": 250},
		{"label": "Nominal", "fieldname": "nominal", "fieldtype": "Currency", "width": 130},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
	]


def get_data(filters):
	rows = []
	kategori = filters.get("kategori")

	if not kategori or kategori == "Petty Cash":
		conditions = []
		values = {}
		if filters.get("from_date"):
			conditions.append("tanggal >= %(from_date)s")
			values["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			conditions.append("tanggal <= %(to_date)s")
			values["to_date"] = filters["to_date"]
		where_clause = " AND " + " AND ".join(conditions) if conditions else ""
		petty_cash = frappe.db.sql(
			f"""
			SELECT name, tanggal, item, nominal, status
			FROM `tabPetty Cash Entry`
			WHERE 1=1 {where_clause}
			""",
			values,
			as_dict=1,
		)
		for pc in petty_cash:
			rows.append({
				"tanggal": pc.tanggal,
				"kategori": "Petty Cash",
				"referensi": pc.name,
				"keterangan": pc.item,
				"nominal": pc.nominal,
				"status": pc.status,
			})

	if not kategori or kategori == "Journal Entry":
		conditions = ["docstatus = 1"]
		values = {}
		if filters.get("from_date"):
			conditions.append("posting_date >= %(from_date)s")
			values["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			conditions.append("posting_date <= %(to_date)s")
			values["to_date"] = filters["to_date"]
		where_clause = " AND ".join(conditions)
		journal_entries = frappe.db.sql(
			f"""
			SELECT name, posting_date, user_remark, total_debit
			FROM `tabJournal Entry`
			WHERE {where_clause}
			""",
			values,
			as_dict=1,
		)
		for je in journal_entries:
			rows.append({
				"tanggal": je.posting_date,
				"kategori": "Journal Entry",
				"referensi": je.name,
				"keterangan": je.user_remark,
				"nominal": je.total_debit,
				"status": "Submitted",
			})

	rows.sort(key=lambda r: r["tanggal"], reverse=True)
	return rows
