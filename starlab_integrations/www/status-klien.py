import frappe
from erpnext.controllers.website_list_for_contact import get_parents_for_user

no_cache = 1


def get_context(context):
	# TSD Bagian 9 (Sprint 9): "Client Portal (status LHU & Invoice untuk
	# klien)". Sales Invoice sudah punya portal native ERPNext sendiri
	# (/invoices) -- halaman ini melengkapi sisi LHU yang belum ada portal-nya
	# sama sekali, plus ringkasan Invoice supaya klien tidak perlu buka 2
	# halaman terpisah.
	#
	# Pemetaan user portal -> Customer memakai mekanisme "Portal User" bawaan
	# ERPNext (Customer > tab Portal Users) -- sama persis dengan yang dipakai
	# /orders dan /invoices, bukan logika baru.
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/status-klien"
		raise frappe.Redirect

	customers = get_parents_for_user("Customer")
	if not customers:
		context.no_access = True
		return context

	context.lhu_list = frappe.get_all(
		"LHU",
		filters={"customer": ["in", customers]},
		fields=["name", "work_order", "tanggal_terbit", "status", "file_lhu"],
		order_by="tanggal_terbit desc",
	)
	context.invoice_list = frappe.get_all(
		"Sales Invoice",
		filters={"customer": ["in", customers], "docstatus": 1},
		fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status"],
		order_by="posting_date desc",
	)
	return context
