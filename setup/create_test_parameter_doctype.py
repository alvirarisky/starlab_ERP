import frappe


def execute():
	if frappe.db.exists("DocType", "Test Parameter"):
		print("Test Parameter DocType already exists, skipping.")
		return

	doc = frappe.get_doc({
		"doctype": "DocType",
		"name": "Test Parameter",
		"module": "Starlab Lab Ops",
		"custom": 0,
		"autoname": "field:parameter_name",
		"naming_rule": "By fieldname",
		"sort_field": "modified",
		"sort_order": "DESC",
		"fields": [
			{
				"fieldname": "parameter_name",
				"label": "Nama Parameter",
				"fieldtype": "Data",
				"reqd": 1,
				"unique": 1,
				"in_list_view": 1,
			},
			{
				"fieldname": "matriks",
				"label": "Matriks",
				"fieldtype": "Select",
				"options": "Udara Ambien\nUdara Emisi\nAir Permukaan\nAir Bersih\nAir Limbah\nTanah\nSedimen\nKebisingan",
				"reqd": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
			},
			{
				"fieldname": "regulasi_acuan",
				"label": "Regulasi Acuan",
				"fieldtype": "Data",
				"reqd": 1,
			},
			# NOTE: metode_uji (Link -> Document Master) sesuai TSD 4.1 sengaja belum
			# ditambahkan di sini. Document Master baru dibuat sebagai stub di Fase 2
			# (app starlab_quality). Frappe menolak Link field yang options-nya
			# menunjuk ke DocType yang belum ada (WrongOptionsDoctypeLinkError).
			# TODO(Fase 2): tambahkan field ini via Customize Form / migration begitu
			# Document Master sudah ada.
			{
				"fieldname": "satuan",
				"label": "Satuan",
				"fieldtype": "Data",
				"reqd": 1,
			},
			{
				"fieldname": "harga_satuan_default",
				"label": "Harga Satuan Default",
				"fieldtype": "Currency",
				"reqd": 0,
			},
			{
				"fieldname": "status",
				"label": "Status",
				"fieldtype": "Select",
				"options": "Aktif\nNonaktif",
				"default": "Aktif",
				"reqd": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
			},
		],
		"permissions": [
			{
				"role": "System Manager",
				"read": 1, "write": 1, "create": 1, "delete": 1,
				"report": 1, "export": 1, "print": 1, "email": 1,
			},
		],
	})
	doc.insert()
	frappe.db.commit()
	print("Test Parameter DocType created.")
