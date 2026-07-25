import frappe
from frappe.utils import getdate, nowdate


def validate_work_order(doc, method=None):
	before = doc.get_doc_before_save()
	previous_status = before.status if before else None
	just_reopened = previous_status == "Completed" and doc.status == "In Progress"

	if just_reopened and not doc.alasan_buka_kembali:
		frappe.throw(frappe._("Alasan Buka Kembali wajib diisi"))


def on_update_work_order(doc, method=None):
	# Auto-complete runs as a direct DB write (not doc.status = ... + save)
	# because Frappe's workflow engine gates any change to the workflow
	# state field on the *saving user* having a matching Transition -- the
	# analyst updating a child row's status_pengujian to "Done" has no
	# "Selesaikan" transition of their own, so a normal save would be
	# blocked. db_set bypasses that check, which is the intended behaviour
	# for a system-triggered auto-transition (not a manual workflow action).
	if doc.status != "In Progress" or not doc.wo_parameter_detail:
		return
	if all(row.status_pengujian == "Done" for row in doc.wo_parameter_detail):
		doc.db_set("status", "Completed", notify=True)


def validate_sample(doc, method=None):
	before = doc.get_doc_before_save()
	previous_status = before.status if before else None

	# Guard for the "Musnahkan" transition -- kept here rather than as a
	# Workflow Transition "condition" because that sandbox evaluates
	# tanggal_musnah inconsistently (sometimes a date object, sometimes a
	# string depending on the call site), which throws a TypeError.
	if previous_status == "Diarsipkan" and doc.status == "Dimusnahkan":
		if doc.retensi != "Bisa Dibuang":
			frappe.throw(frappe._("Sample hanya bisa dimusnahkan kalau retensi = Bisa Dibuang"))
		if not doc.tanggal_musnah or getdate(doc.tanggal_musnah) > getdate(nowdate()):
			frappe.throw(frappe._("Tanggal Pemusnahan belum terlewati"))

	if doc.status != "Diterima" or not doc.work_order:
		return

	wo_status = frappe.db.get_value("Work Order Pengujian", doc.work_order, "status")
	if wo_status == "Approved":
		frappe.db.set_value("Work Order Pengujian", doc.work_order, "status", "In Progress")


def on_update_test_result(doc, method=None):
	if doc.status != "Divalidasi" or not doc.sample:
		return

	statuses = frappe.get_all("Test Result", filters={"sample": doc.sample}, pluck="status")
	if statuses and all(s == "Divalidasi" for s in statuses):
		sample_status = frappe.db.get_value("Sample", doc.sample, "status")
		if sample_status == "Sedang Diuji":
			frappe.db.set_value("Sample", doc.sample, "status", "Divalidasi")
