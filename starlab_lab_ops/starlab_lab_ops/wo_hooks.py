import frappe
from frappe.utils import flt, getdate, nowdate

from starlab_lab_ops.audit_log import log_system_field_change

# db_set()/frappe.db.set_value() calls below intentionally bypass the
# Workflow engine (see comments at each call site) for system-triggered
# auto-transitions. log_system_field_change (starlab_lab_ops/audit_log.py)
# writes the Version entry that Document.save_version() would have written
# for an equivalent normal save, plus a human-readable Comment, so these
# transitions still show up in the document's Track Changes/timeline.


def validate_work_order(doc, method=None):
	before = doc.get_doc_before_save()
	previous_status = before.status if before else None
	just_reopened = previous_status == "Completed" and doc.status == "In Progress"

	if just_reopened and not doc.alasan_buka_kembali:
		frappe.throw(frappe._("Alasan Buka Kembali wajib diisi"))


def _notify_role(role, subject, message):
	users = frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent")
	if not users:
		return
	# frappe.sendmail raises OutgoingEmailError immediately when no default
	# outgoing Email Account is configured -- must never block the workflow
	# transition/scheduled job that triggered this notification.
	try:
		frappe.sendmail(recipients=users, subject=subject, message=message)
	except Exception:
		frappe.log_error(title="Gagal mengirim notifikasi email", message=frappe.get_traceback())


def on_update_work_order(doc, method=None):
	# TSD Bagian 10 "Approval Pending": Work Order baru dibuat = state Draft
	# menunggu approval Manajer Teknis (transisi "Setujui" -> Approved).
	if not doc.get_doc_before_save() and doc.status == "Draft":
		_notify_role(
			"Manajer Teknis",
			frappe._("Work Order {0} menunggu approval Anda").format(doc.name),
			frappe._("Work Order {0} baru dibuat dan menunggu approval Anda.").format(doc.name),
		)

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
		old_status = doc.status
		doc.db_set("status", "Completed", notify=True)
		log_system_field_change(
			doc.doctype,
			doc.name,
			{"status": (old_status, "Completed")},
			frappe._(
				"Status otomatis diubah ke Completed oleh sistem karena seluruh parameter pengujian sudah Done."
			),
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
		log_system_field_change(
			"Work Order Pengujian",
			doc.work_order,
			{"status": (wo_status, "In Progress")},
			frappe._("Status otomatis diubah ke In Progress oleh sistem karena Sample {0} diterima.").format(
				doc.name
			),
		)


def validate_test_result(doc, method=None):
	# TSD SS6.5: reject (Diajukan Validasi -> Ditolak) wajib mengisi
	# catatan_validasi.
	before = doc.get_doc_before_save()
	if (
		before
		and before.status == "Diajukan Validasi"
		and doc.status == "Ditolak"
		and not doc.catatan_validasi
	):
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

	fields = (
		"qc_type",
		"nilai_slope",
		"nilai_intersep",
		"nilai_r2",
		"nilai_rpd_persen",
		"nilai_trueness_persen",
	)
	for row_before, row_after in zip(before_rows, after_rows):
		if any(row_before.get(f) != row_after.get(f) for f in fields):
			return True
	return False


def on_update_test_result(doc, method=None):
	before = doc.get_doc_before_save()

	# TSD Bagian 10 "Approval Pending": notifikasi Manajer Teknis begitu Test
	# Result diajukan untuk validasi.
	if before and before.status != "Diajukan Validasi" and doc.status == "Diajukan Validasi":
		_notify_role(
			"Manajer Teknis",
			frappe._("Test Result {0} menunggu validasi Anda").format(doc.name),
			frappe._("Test Result {0} sudah diajukan dan menunggu validasi Anda.").format(doc.name),
		)

	# TSD Bagian 10 "Test Result Ditolak": notifikasi ke analis pembuatnya.
	if before and before.status != "Ditolak" and doc.status == "Ditolak" and doc.owner:
		try:
			frappe.sendmail(
				recipients=[doc.owner],
				subject=frappe._("Test Result {0} ditolak").format(doc.name),
				message=frappe._("Test Result {0} ditolak oleh Manajer Teknis. Catatan: {1}").format(
					doc.name, doc.catatan_validasi or "-"
				),
			)
		except Exception:
			frappe.log_error(title="Gagal mengirim notifikasi email", message=frappe.get_traceback())

	if doc.status != "Divalidasi" or not doc.sample:
		return

	statuses = frappe.get_all("Test Result", filters={"sample": doc.sample}, pluck="status")
	if statuses and all(s == "Divalidasi" for s in statuses):
		sample_status = frappe.db.get_value("Sample", doc.sample, "status")
		if sample_status == "Sedang Diuji":
			frappe.db.set_value("Sample", doc.sample, "status", "Divalidasi")
			log_system_field_change(
				"Sample",
				doc.sample,
				{"status": (sample_status, "Divalidasi")},
				frappe._(
					"Status otomatis diubah ke Divalidasi oleh sistem karena seluruh Test Result sudah Divalidasi."
				),
			)
