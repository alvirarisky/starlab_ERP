import frappe
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "Bulan", "fieldname": "bulan", "fieldtype": "Data", "width": 100},
		{"label": "Quotation Dibuat", "fieldname": "quotation_dibuat", "fieldtype": "Int", "width": 140},
		{"label": "Quotation dengan Work Order", "fieldname": "wo_dibuat", "fieldtype": "Int", "width": 180},
		{"label": "Conversion Rate", "fieldname": "conversion_rate", "fieldtype": "Percent", "width": 130},
	]


def get_data(filters):
	# Sengaja Query Report, bukan Number Card sederhana -- Number Card
	# "Document Type" cuma bisa COUNT/SUM satu DocType langsung, tidak bisa
	# menghitung "berapa % Quotation yang PUNYA Work Order terkait"
	# (butuh JOIN + agregasi per bulan), jadi angka yang dihasilkan Number
	# Card biasa untuk metrik ini pasti salah/menyesatkan (lihat catatan di
	# docs/ringkasan-seluruh-sprint.md Bagian 6 & jobdesc_pira.md item 6).
	conditions = ["q.docstatus < 2"]
	values = {}
	if filters.get("from_date"):
		conditions.append("q.transaction_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("q.transaction_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	where_clause = " AND ".join(conditions)

	rows = frappe.db.sql(
		f"""
		SELECT
			DATE_FORMAT(q.transaction_date, '%%Y-%%m') AS bulan,
			COUNT(DISTINCT q.name) AS quotation_dibuat,
			COUNT(DISTINCT wo.quotation) AS wo_dibuat
		FROM `tabQuotation` q
		LEFT JOIN `tabWork Order Pengujian` wo ON wo.quotation = q.name
		WHERE {where_clause}
		GROUP BY bulan
		ORDER BY bulan DESC
		""",
		values,
		as_dict=1,
	)

	for row in rows:
		row["conversion_rate"] = (
			flt(row["wo_dibuat"]) / flt(row["quotation_dibuat"]) * 100 if row["quotation_dibuat"] else 0
		)

	return rows
