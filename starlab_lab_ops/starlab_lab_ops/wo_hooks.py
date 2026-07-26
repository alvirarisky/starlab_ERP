import frappe
from frappe.utils import flt, getdate, nowdate


def _log_system_transition(doctype, name, text):
	# db_set()/frappe.db.set_value() below intentionally bypass the Workflow
	# engine (see comments at each call site) and, as a side effect, also
	# bypass Document.save_version() -- these auto-transitions never show up
	# in the Version/Track Changes log. This helper adds a plain Comment so
	# there is at least a human-readable trace of "system did X and why" in
	# the document timeline, without changing the transition behaviour itself.
	frappe.get_doc(
		{
			"doctype": "Comment",
			"comment_type": "Info",
			"reference_doctype": doctype,
			"reference_name": name,
			"content": text,
		}
	).insert(ignore_permissions=True)


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
		doc.add_comment(
			"Info",
			frappe._("Status otomatis diubah ke Completed oleh sistem karena seluruh parameter pengujian sudah Done."),
		)


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
		_log_system_transition(
			"Work Order Pengujian",
			doc.work_order,
			frappe._("Status otomatis diubah ke In Progress oleh sistem karena Sample {0} diterima.").format(doc.name),
		)


def validate_test_result(doc, method=None):
	# TSD SS6.5: reject (Diajukan Validasi -> Ditolak) wajib mengisi
	# catatan_validasi.
	before = doc.get_doc_before_save()
	if before and before.status == "Diajukan Validasi" and doc.status == "Ditolak" and not doc.catatan_validasi:
		frappe.throw(frappe._("Catatan Validasi wajib diisi saat menolak Test Result"))

	# TSD SS5 Non-Functional (Data Integrity): hasil_uji & qc_detail tidak
	# boleh diubah lagi setelah divalidasi. `before.locked and doc.locked`
	# sengaja tidak menghalangi transisi "Batalkan Validasi" -- transisi itu
	# men-set locked=0 lewat Workflow update_field sebelum validate() ini
	# jalan, jadi doc.locked sudah 0 pada titik ini dan kondisinya lolos.
	if before and before.locked and doc.locked:
		if flt(doc.hasil_uji) != flt(before.hasil_uji) or _qc_rows_changed(doc, before):
			frappe.throw(frappe._("Hasil Uji dan Data QC tidak bisa diubah setelah Divalidasi (terkunci)"))


def _qc_rows_changed(doc, before):
	before_rows = before.get("qc_detail") or []
	after_rows = doc.get("qc_detail") or []
	if len(before_rows) != len(after_rows):
		return True

	fields = ("qc_type", "nilai_slope", "nilai_intersep", "nilai_r2", "nilai_rpd_persen", "nilai_trueness_persen")
	for row_before, row_after in zip(before_rows, after_rows):
		if any(row_before.get(f) != row_after.get(f) for f in fields):
			return True
	return False


def on_update_test_result(doc, method=None):
	if doc.status != "Divalidasi" or not doc.sample:
		return

	statuses = frappe.get_all("Test Result", filters={"sample": doc.sample}, pluck="status")
	if statuses and all(s == "Divalidasi" for s in statuses):
		sample_status = frappe.db.get_value("Sample", doc.sample, "status")
		if sample_status == "Sedang Diuji":
			frappe.db.set_value("Sample", doc.sample, "status", "Divalidasi")
			_log_system_transition(
				"Sample",
				doc.sample,
				frappe._("Status otomatis diubah ke Divalidasi oleh sistem karena seluruh Test Result sudah Divalidasi."),
			)
