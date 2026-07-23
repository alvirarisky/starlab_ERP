import frappe


def execute():
	meta = frappe.get_meta("Test Parameter")
	if meta.get_field("metode_uji"):
		print("metode_uji already exists on Test Parameter, skipping.")
		return

	doc = frappe.get_doc("DocType", "Test Parameter")
	doc.append("fields", {
		"fieldname": "metode_uji",
		"label": "Metode Uji",
		"fieldtype": "Link",
		"options": "Document Master",
		"reqd": 0,
		"insert_after": "regulasi_acuan",
	})
	doc.save()
	frappe.db.commit()
	print("metode_uji field added to Test Parameter.")
