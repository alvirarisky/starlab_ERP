import frappe
from frappe.model.workflow import apply_workflow


def sync_client_inquiry_from_kaji_ulang(doc, method=None):
	# Kaji Ulang Tender.on_update -- pushes the linked Client Inquiry's
	# Workflow forward from "Diajukan Kaji Ulang" to "Disetujui MT"/"Ditolak
	# MT" (TSD Bagian 6.1: transisi ini dilakukan "melalui DocType Kaji Ulang
	# Tender terkait", bukan tombol Workflow langsung di Client Inquiry).
	#
	# This goes through frappe.model.workflow.apply_workflow (not a raw
	# db_set/set_value bypass like wo_hooks.py) because the acting user here
	# -- the Manajer Teknis filling in this Kaji Ulang Tender -- genuinely
	# holds the role the transition requires, so there's no reason to skip
	# the normal permission check/versioning/notification apply_workflow
	# already gives us (it also auto-adds a "Workflow" comment on success).
	if not doc.client_inquiry or not doc.rekomendasi:
		return

	client_inquiry = frappe.get_doc("Client Inquiry", doc.client_inquiry)
	if client_inquiry.status != "Diajukan Kaji Ulang":
		# Already resolved (or not submitted for review yet) -- avoid
		# re-triggering the transition/duplicate Quotation Draft on repeat
		# saves of this Kaji Ulang Tender (e.g. editing catatan_kelayakan
		# after the fact).
		return

	if doc.rekomendasi in ("Layak", "Layak dengan Catatan"):
		apply_workflow(client_inquiry, "Setujui")
		_create_quotation_draft(client_inquiry)
	elif doc.rekomendasi == "Tidak Layak":
		apply_workflow(client_inquiry, "Tolak")


def _create_quotation_draft(client_inquiry):
	# [PRD v8 Sprint 12] Form A/client_inquiry sekarang WAJIB di Quotation --
	# fungsi ini sudah selalu mengisinya (lihat quotation.client_inquiry di
	# bawah), jadi tidak perlu perubahan untuk itu. Yang masih perlu
	# di-guard: kalau Client Inquiry ini belum tertaut ke Customer
	# terdaftar, auto-create tetap tidak dipaksakan (Quotation core ERPNext
	# mewajibkan party_name) -- cukup catat di timeline supaya Administrasi
	# tahu harus membuat Quotation manual (tetap wajib mengisi Referensi
	# Form A sendiri di form manual itu).
	if not client_inquiry.customer:
		client_inquiry.add_comment(
			"Info",
			frappe._(
				"Kaji Ulang Tender merekomendasikan Layak, tapi Quotation Draft tidak dibuat "
				"otomatis karena Client Inquiry ini belum tertaut ke Customer terdaftar. "
				"Administrasi perlu membuat Quotation secara manual dan mengisi Referensi Form A."
			),
		)
		return

	# Auto-created server-side (no Desk form to pull the user's default
	# Company from), so it has to be set explicitly here or core
	# AccountsController validation throws "Please select a Company". If
	# the site has no default Company configured (multi-company setup, or
	# Setup Wizard not finished), degrade the same way as the no-Customer
	# case above instead of letting that core error abort this save.
	default_company = frappe.defaults.get_global_default("company")
	if not default_company:
		client_inquiry.add_comment(
			"Info",
			frappe._(
				"Kaji Ulang Tender merekomendasikan Layak, tapi Quotation Draft tidak dibuat "
				"otomatis karena tidak ada Company default yang terkonfigurasi di site ini. "
				"Administrasi perlu membuat Quotation secara manual dan mengisi Referensi Form A."
			),
		)
		return

	quotation = frappe.new_doc("Quotation")
	quotation.quotation_to = "Customer"
	quotation.party_name = client_inquiry.customer
	quotation.client_inquiry = client_inquiry.name
	quotation.company = default_company
	for row in client_inquiry.parameter_diminta:
		quotation.append(
			"parameter_detail",
			{
				"parameter": row.parameter,
				"frekuensi": 1,
				"qty_per_titik": client_inquiry.estimasi_qty or 1,
			},
		)
	# Desk normally fills currency/price list/taxes/contact & address details
	# the moment a Customer is picked on a new Quotation (client-side
	# triggers calling erpnext.accounts.party.get_party_details under the
	# hood). Creating the doc server-side skips all of that, so pull it in
	# explicitly -- otherwise core total/currency calculations in
	# AccountsController.validate() blow up on missing values.
	quotation.run_method("set_missing_values")

	# This whole block runs inside Kaji Ulang Tender.on_update, so any
	# unhandled error here (e.g. a core Quotation validation quirk we
	# haven't hit yet -- Quotation's standard "items" table is `reqd=1`
	# in ERPNext core but SAI's own line items live entirely in
	# parameter_detail, so a Quotation with zero standard Item rows can
	# fail core totals validation) would abort the Manajer Teknis's Kaji
	# Ulang Tender save itself. Auto-creating the Quotation Draft is a
	# convenience on top of that primary action, not a prerequisite for
	# it, so any failure here must degrade to a manual-creation note
	# instead of blocking the save.
	savepoint = "before_auto_quotation_draft"
	frappe.db.savepoint(savepoint)
	try:
		quotation.insert(ignore_permissions=True)
		quotation.add_comment(
			"Info",
			frappe._(
				"Quotation Draft ini dibuat otomatis dari Client Inquiry {0} setelah Kaji Ulang "
				"Tender merekomendasikan Layak/Layak dengan Catatan."
			).format(client_inquiry.name),
		)
	except Exception:
		frappe.db.rollback(save_point=savepoint)
		frappe.log_error(
			title="Auto-create Quotation Draft dari Client Inquiry gagal",
			message=frappe.get_traceback(),
		)
		client_inquiry.add_comment(
			"Info",
			frappe._(
				"Kaji Ulang Tender merekomendasikan Layak, tapi Quotation Draft gagal dibuat "
				"otomatis (lihat Error Log). Administrasi perlu membuat Quotation secara manual "
				"dan mengisi Referensi Form A."
			),
		)
