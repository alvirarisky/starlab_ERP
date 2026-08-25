import frappe

from starlab_lab_ops.audit_log import log_system_field_change
from starlab_lab_ops.wo_hooks import _notify_role

ROLE_BY_STATUS = {
	"Menunggu Approval MT": "Manajer Teknis",
	"Menunggu Approval MM": "Manajer Mutu",
	"Menunggu Approval Direksi": "Direksi",
}


def validate_wo_eksternal(doc, method=None):
	# Frappe Workflow Transition "condition" jalan lewat safe_eval, yang cuma
	# mengekspos float/int/long/round (lihat WHITELISTED_SAFE_EVAL_GLOBALS di
	# frappe.utils.safe_exec) -- TIDAK ada all()/any()/len(), jadi pengecekan
	# "semua baris parameter_detail sudah punya sample" tidak bisa lewat
	# condition transisi "Ajukan" (dicoba dulu, crash NameError di SETIAP
	# save, bukan cuma pas transisi itu -- Frappe mengevaluasi seluruh
	# transisi keluar dari state saat ini setiap on_update, bukan cuma yang
	# sedang dijalankan). Dipindah ke sini, Python biasa, all() aman dipakai.
	before = doc.get_doc_before_save()
	leaving_draft = before and before.status == "Draft" and doc.status != "Draft"
	if not leaving_draft:
		return

	missing = []
	if not doc.vendor_nama:
		missing.append(frappe._("Nama Vendor/Lab Subkon"))
	if not doc.tanggal_kirim:
		missing.append(frappe._("Tanggal Kirim ke Vendor"))
	if not doc.tanggal_target_kembali:
		missing.append(frappe._("Tanggal Target Kembali"))
	if not doc.pj_penerima_hasil:
		missing.append(frappe._("PJ Penerima Hasil"))
	if not all(row.sample for row in doc.parameter_detail):
		missing.append(frappe._("Sample (di setiap baris Detail Parameter Subkon)"))

	if missing:
		frappe.throw(frappe._("Lengkapi dulu sebelum diajukan approval: {0}").format(", ".join(missing)))


def create_draft_wo_eksternal(wo_doc, rows):
	woe = frappe.new_doc("WO Eksternal")
	woe.work_order = wo_doc.name
	woe.status = "Draft"
	for row in rows:
		woe.append("parameter_detail", {"parameter": row.parameter})
	woe.insert(ignore_permissions=True)

	for row in rows:
		frappe.db.set_value("WO Parameter Detail", row.name, "wo_eksternal", woe.name)

	_notify_role(
		"Administrasi",
		frappe._("WO Eksternal {0} perlu dilengkapi").format(woe.name),
		frappe._(
			"WO Eksternal {0} otomatis dibuat karena ada parameter yang ditandai Subkon di"
			" Work Order {1}. Mohon lengkapi vendor, biaya, sample, dan tanggal sebelum"
			" mengajukan approval."
		).format(woe.name, wo_doc.name),
	)


def on_update_wo_eksternal(doc, method=None):
	before = doc.get_doc_before_save()

	# TSD Bagian 10 "Approval Pending" (pola sama seperti quotation_hooks.on_update):
	# notifikasi segera begitu WO Eksternal masuk ke tahap approval berikutnya.
	if before and before.status != doc.status:
		role = ROLE_BY_STATUS.get(doc.status)
		if role:
			_notify_role(
				role,
				frappe._("WO Eksternal {0} menunggu approval Anda").format(doc.name),
				frappe._("WO Eksternal {0} sudah masuk ke tahap approval Anda ({1}).").format(
					doc.name, doc.status
				),
			)

	# Open question #1 (jawaban Starlab): hasil subkon yang sudah balik harus
	# ikut ke LHU. Daripada mengubah lhu_hooks.populate_test_result_list,
	# begitu hasil ditandai Diterima pada WO Eksternal yang sudah Approved,
	# sistem membuat Test Result normal (status Diajukan Validasi) supaya
	# tetap lewat validasi Manajer Teknis seperti biasa -- bukan lompat
	# langsung ke Divalidasi -- lalu otomatis ke-include lewat pipeline LHU
	# yang sudah ada tanpa perubahan apa pun di lhu_hooks.py.
	if doc.status != "Approved":
		return

	for row in doc.parameter_detail:
		if row.status_hasil != "Diterima" or not row.sample or row.test_result:
			continue
		if row.hasil_uji in (None, ""):
			continue

		test_result = frappe.new_doc("Test Result")
		test_result.sample = row.sample
		test_result.parameter = row.parameter
		test_result.analis = doc.pj_penerima_hasil
		test_result.hasil_uji = row.hasil_uji
		test_result.insert(ignore_permissions=True)

		# Test Result punya Workflow sendiri (Draft -> Diajukan Validasi -> ...) --
		# insert() langsung dengan status non-Draft ditolak WorkflowPermissionError
		# (Frappe cuma izinkan doc baru mulai dari state awal Workflow). db_set +
		# log_system_field_change adalah pola baku codebase ini untuk transisi
		# system-triggered (lihat komentar di wo_hooks.py) -- analis lab tidak
		# pernah benar-benar "mengajukan" hasil subkon ini secara manual.
		old_status = test_result.status
		test_result.db_set("status", "Diajukan Validasi", notify=True)
		log_system_field_change(
			"Test Result",
			test_result.name,
			{"status": (old_status, "Diajukan Validasi")},
			frappe._(
				"Status otomatis diubah ke Diajukan Validasi oleh sistem karena hasil"
				" subkon WO Eksternal {0} sudah ditandai Diterima."
			).format(doc.name),
		)

		frappe.db.set_value("WO Eksternal Parameter Detail", row.name, "test_result", test_result.name)
