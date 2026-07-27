import frappe
from frappe.utils import add_days


def set_due_date(doc, method=None):
	# PRD v8 Sprint 12, item 7 / TSD Bab 6.7: Term of Payment default SAI --
	# due_date = tanggal invoice terbit + 7 hari kalender, dikonfirmasi PO
	# (terpisah dari DP 50% di muka yang sudah diatur di T&C Quotation).
	# docstatus==0 guard sama seperti tanggal_kadaluwarsa Quotation -- sekali
	# submitted, due_date tidak lagi dihitung ulang diam-diam kalau
	# posting_date pernah diubah pasca-submit (amend, dst).
	if doc.posting_date and doc.docstatus == 0:
		doc.due_date = add_days(doc.posting_date, 7)


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
