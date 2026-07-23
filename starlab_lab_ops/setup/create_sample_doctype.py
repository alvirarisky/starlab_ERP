import frappe

MODULE = "Starlab Lab Ops"
MATRIKS_OPTIONS = "Udara Ambien\nUdara Emisi\nAir Permukaan\nAir Bersih\nAir Limbah\nTanah\nSedimen\nKebisingan"


def execute():
	if frappe.db.exists("DocType", "Sample"):
		print("Sample already exists, skipping.")
		return

	doc = frappe.get_doc({
		"doctype": "DocType",
		"name": "Sample",
		"module": MODULE,
		"custom": 0,
		"autoname": "field:sample_id",
		"naming_rule": "By fieldname",
		"track_changes": 1,
		"sort_field": "modified",
		"sort_order": "DESC",
		"fields": [
			{"fieldname": "sample_id", "label": "ID Sample", "fieldtype": "Data", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "work_order", "label": "Work Order", "fieldtype": "Link", "options": "Work Order Pengujian", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "matriks", "label": "Matriks", "fieldtype": "Select", "options": MATRIKS_OPTIONS, "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "tanggal_terima", "label": "Tanggal Terima", "fieldtype": "Date", "reqd": 1, "in_list_view": 1},
			{"fieldname": "status", "label": "Status", "fieldtype": "Select",
			 "options": "Diterima\nSedang Diuji\nDivalidasi\nDiarsipkan\nDimusnahkan", "reqd": 1, "default": "Diterima",
			 "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "retensi", "label": "Retensi", "fieldtype": "Select", "options": "Tahan\nBisa Dibuang", "reqd": 1, "in_standard_filter": 1},
			{"fieldname": "tanggal_musnah", "label": "Tanggal Musnah", "fieldtype": "Date"},
			{"fieldname": "catatan_kondisi", "label": "Catatan Kondisi", "fieldtype": "Small Text"},
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1, "email": 1, "share": 1},
		],
	})
	doc.insert()
	frappe.db.commit()
	print("Sample DocType created.")
