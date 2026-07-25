from frappe.utils import add_days


def validate(doc, method=None):
	for row in doc.get("parameter_detail") or []:
		row.harga_total = (row.frekuensi or 0) * (row.qty_per_titik or 0) * (row.harga_satuan or 0)

	if doc.transaction_date:
		doc.tanggal_kadaluwarsa = add_days(doc.transaction_date, 30)
