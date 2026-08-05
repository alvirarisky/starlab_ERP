import frappe

from starlab_lab_ops.audit_log import log_system_field_change


def get_permission_query_conditions(user=None):
	# Client Portal (starlab_integrations/www/status-klien.py) query LHU
	# lewat frappe.get_all tanpa ignore_permissions -- role Customer butuh
	# "read" doctype-level (lihat lhu.json permissions) supaya tidak
	# PermissionError, TAPI tanpa filter row-level di sini, itu berarti
	# Customer manapun bisa baca LHU company LAIN lewat API langsung
	# (/api/resource/LHU/<name>), bukan cuma lewat halaman portal yang sudah
	# memfilter di query-nya sendiri. Filter di bawah menutup celah itu --
	# pola sama seperti starlab_quality.document_control_hooks.
	user = user or frappe.session.user
	roles = frappe.get_roles(user)
	if "Customer" not in roles or "System Manager" in roles:
		return ""

	from erpnext.controllers.website_list_for_contact import get_parents_for_user

	customers = get_parents_for_user("Customer")
	if not customers:
		return "1=0"

	customers_sql = ", ".join(frappe.db.escape(c) for c in customers)
	return f"`tabLHU`.customer in ({customers_sql})"


def has_permission(doc, ptype=None, user=None):
	user = user or frappe.session.user
	roles = frappe.get_roles(user)
	if "Customer" not in roles or "System Manager" in roles:
		return True

	# Customer tidak punya write/create/delete di lhu.json permissions sama
	# sekali, jadi ptype selain "read" semestinya sudah ditolak base
	# permission duluan -- pengecekan di sini murni row-level scoping baca.
	if ptype and ptype != "read":
		return False

	from erpnext.controllers.website_list_for_contact import get_parents_for_user

	customers = get_parents_for_user("Customer")
	return doc.customer in customers


def populate_test_result_list(doc, method=None):
	# TSD Bagian 5 (relationship design): "LHU (agregasi Test Result
	# tervalidasi)". Sebelumnya tidak ada apa pun yang mengisi
	# test_result_list otomatis -- Manajer Mutu harus link satu-satu manual.
	# Hanya jalan sekali (saat list masih kosong) supaya tidak menimpa
	# penyesuaian manual yang sudah dilakukan di LHU yang sudah ada.
	if doc.test_result_list or not doc.work_order:
		return

	test_results = frappe.get_all(
		"Test Result",
		filters={"work_order": doc.work_order, "status": "Divalidasi"},
		fields=["name", "parameter"],
	)
	if not test_results:
		return

	# metode_acuan idealnya fetch dari Test Parameter.regulasi_acuan lewat
	# Test Result.parameter (2 level), tapi fetch_from Frappe cuma dukung
	# 1 level -- diisi manual di sini (TODO lama dari setup script Fase 2
	# akhirnya diselesaikan di titik ini, bukan lewat Server Script terpisah).
	# Batch di-fetch sekali untuk semua parameter yang muncul, bukan satu
	# get_value per baris Test Result.
	parameter_names = {row.parameter for row in test_results if row.parameter}
	regulasi_by_parameter = (
		{
			p.name: p.regulasi_acuan
			for p in frappe.get_all(
				"Test Parameter", filters={"name": ["in", list(parameter_names)]}, fields=["name", "regulasi_acuan"]
			)
		}
		if parameter_names
		else {}
	)
	for row in test_results:
		doc.append(
			"test_result_list",
			{
				"test_result": row.name,
				"metode_acuan": regulasi_by_parameter.get(row.parameter),
			},
		)


def before_insert(doc, method=None):
	# Draft hasil "Amend" (native ERPNext, dipicu dari Cancel lalu tombol
	# Amend) sudah punya amended_from terisi sejak sebelum insert -- pakai
	# ini untuk membedakan "revisi dari LHU lama" vs LHU baru murni, karena
	# field status sekarang read_only/dikontrol sistem sepenuhnya (lihat
	# on_submit di bawah untuk Issued/Superseded).
	if doc.amended_from:
		doc.status = "Revised"


def on_submit(doc, method=None):
	old_status = doc.status
	doc.db_set("status", "Issued")
	log_system_field_change(doc.doctype, doc.name, {"status": (old_status, "Issued")})

	# LHU lama yang di-amend baru resmi "Superseded" begitu LHU pengganti
	# ini benar-benar terbit (submit), bukan langsung saat Cancel/Amend --
	# supaya tidak ada jeda di mana LHU lama sudah "usang" padahal LHU
	# pengganti belum tentu jadi diterbitkan. db_set (bukan .save()) karena
	# LHU lama sudah docstatus=2 (cancelled), tidak bisa disimpan normal.
	if doc.amended_from:
		old_amended_status = frappe.db.get_value("LHU", doc.amended_from, "status")
		frappe.db.set_value("LHU", doc.amended_from, "status", "Superseded")
		log_system_field_change(
			"LHU",
			doc.amended_from,
			{"status": (old_amended_status, "Superseded")},
			frappe._("Status otomatis diubah ke Superseded oleh sistem karena digantikan oleh {0}.").format(doc.name),
		)
