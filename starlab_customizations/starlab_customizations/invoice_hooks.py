import frappe


@frappe.whitelist()
def get_existing_invoice_for_lhu(lhu: str) -> str | None:
	# Read-only lookup so the "Buat Invoice" button can route to an existing
	# Sales Invoice instead of creating a duplicate for the same LHU. Actual
	# invoice creation happens client-side as an unsaved new doc (see lhu.js)
	# -- Sales Invoice's standard `items` table is mandatory even at insert
	# time (not just submit), and Test Parameter isn't linked to an Item
	# master yet (same open question as Quotation Parameter Detail's
	# harga_satuan), so there's no safe way to insert a Sales Invoice here
	# with zero items. Administrasi fills in item & harga themselves on the
	# prefilled form before saving.
	lhu_doc = frappe.get_doc("LHU", lhu)
	lhu_doc.check_permission("read")
	return frappe.db.get_value("Sales Invoice", {"lhu": lhu_doc.name, "docstatus": ["!=", 2]}, "name")
