import frappe


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 220},
		{"label": "Total Quotation", "fieldname": "total_quotation", "fieldtype": "Int", "width": 130},
		{"label": "Total Work Order", "fieldname": "total_wo", "fieldtype": "Int", "width": 130},
		{"label": "Total LHU Terbit", "fieldname": "total_lhu", "fieldtype": "Int", "width": 130},
		{"label": "Order Terakhir", "fieldname": "order_terakhir", "fieldtype": "Date", "width": 130},
	]


def get_data(filters):
	# Sengaja Query Report, bukan Number Card -- histori per klien butuh
	# JOIN lintas 3 DocType (Quotation/Work Order Pengujian/LHU) dan
	# di-group per Customer, bukan agregat tunggal (lihat catatan di
	# docs/ringkasan-seluruh-sprint.md Bagian 6 & jobdesc_pira.md item 6).
	conditions = ["q.quotation_to = 'Customer'", "q.docstatus < 2"]
	values = {}
	if filters.get("customer"):
		conditions.append("q.party_name = %(customer)s")
		values["customer"] = filters["customer"]
	if filters.get("from_date"):
		conditions.append("q.transaction_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("q.transaction_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	where_clause = " AND ".join(conditions)

	return frappe.db.sql(
		f"""
		SELECT
			q.party_name AS customer,
			COUNT(DISTINCT q.name) AS total_quotation,
			COUNT(DISTINCT wo.name) AS total_wo,
			COUNT(DISTINCT CASE WHEN lhu.status IN ('Issued', 'Revised') THEN lhu.name END) AS total_lhu,
			MAX(q.transaction_date) AS order_terakhir
		FROM `tabQuotation` q
		LEFT JOIN `tabWork Order Pengujian` wo ON wo.quotation = q.name
		LEFT JOIN `tabLHU` lhu ON lhu.work_order = wo.name
		WHERE {where_clause}
		GROUP BY q.party_name
		ORDER BY order_terakhir DESC
		""",
		values,
		as_dict=1,
	)
