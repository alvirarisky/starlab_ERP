import frappe

MODULE = "Starlab Customizations"


def execute():
	if frappe.db.exists("DocType", "Petty Cash Entry"):
		print("Petty Cash Entry already exists, skipping.")
		return

	doc = frappe.get_doc({
		"doctype": "DocType",
		"name": "Petty Cash Entry",
		"module": MODULE,
		"custom": 0,
		"track_changes": 1,
		"sort_field": "modified",
		"sort_order": "DESC",
		"fields": [
			{"fieldname": "tanggal", "label": "Tanggal", "fieldtype": "Date", "reqd": 1, "in_list_view": 1},
			{"fieldname": "item", "label": "Item", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
			{"fieldname": "nominal", "label": "Nominal", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1},
			{"fieldname": "bukti", "label": "Bukti", "fieldtype": "Attach Image", "reqd": 1},
			{"fieldname": "keterangan", "label": "Keterangan", "fieldtype": "Small Text"},
			{"fieldname": "status", "label": "Status", "fieldtype": "Select",
			 "options": "Draft\nMenunggu Approval\nDisetujui\nDitolak", "reqd": 1, "default": "Draft",
			 "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "journal_entry", "label": "Journal Entry", "fieldtype": "Link", "options": "Journal Entry", "read_only": 1},
			{"fieldname": "disetujui_oleh", "label": "Disetujui Oleh", "fieldtype": "Link", "options": "Employee"},
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1, "email": 1, "share": 1},
		],
	})
	doc.insert()
	frappe.db.commit()
	print("Petty Cash Entry DocType created.")
