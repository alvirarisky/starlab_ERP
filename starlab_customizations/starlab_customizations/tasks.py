import frappe
from frappe.utils import add_to_date, now_datetime, nowdate

from starlab_customizations.audit_log import log_system_field_change


def _safe_sendmail(recipients, subject, message):
	# frappe.sendmail raises OutgoingEmailError immediately (not just a
	# queued/deferred failure) when no default outgoing Email Account is
	# configured -- a real risk on a fresh site. A notification failing to
	# send must never block whatever workflow transition/scheduled job
	# triggered it.
	try:
		frappe.sendmail(recipients=recipients, subject=subject, message=message)
	except Exception:
		frappe.log_error(title="Gagal mengirim notifikasi email", message=frappe.get_traceback())


PENDING_APPROVAL_STATES = [
	"Menunggu Approval MT",
	"Menunggu Approval MM",
	"Menunggu Approval Direksi",
]

ROLE_BY_STATE = {
	"Menunggu Approval MT": "Manajer Teknis",
	"Menunggu Approval MM": "Manajer Mutu",
	"Menunggu Approval Direksi": "Direksi",
}


def check_quotation_sla():
	# PRD v6 SS5.5 -- eskalasi otomatis kalau approval Quotation macet >1x24 jam.
	#
	# Target eskalasi (PRD v6 Open Question #1) sudah dijawab PO di PRD v8:
	# reminder ulang ke approver yang sama pada state saat ini (role lewat
	# ROLE_BY_STATE). Ini KEPUTUSAN FINAL PO, bukan default sementara yang
	# menunggu konfirmasi lagi -- jangan diganti ke opsi "atasan approver"
	# atau "langsung ke Direksi" tanpa keputusan PO baru yang eksplisit.
	cutoff = add_to_date(now_datetime(), hours=-24, as_string=False)
	quotations = frappe.get_all(
		"Quotation",
		filters={
			"workflow_state": ["in", PENDING_APPROVAL_STATES],
			"workflow_state_since": ["<", cutoff],
			"eskalasi_terkirim": 0,
			"docstatus": ["<", 2],
		},
		fields=["name", "workflow_state"],
	)
	role_users_cache = {}
	for row in quotations:
		_notify_pending_approver(row.name, row.workflow_state, role_users_cache)
		frappe.db.set_value("Quotation", row.name, "eskalasi_terkirim", 1)


HAS_ROLE_DOCTYPE = "Has Role"


def _get_role_users(role, cache):
	# Dipanggil di dalam loop per-baris (check_quotation_sla/
	# check_invoice_due/check_invoice_overdue) -- role peserta approval/
	# reminder biasanya sama untuk banyak baris sekaligus dalam satu run
	# scheduled job, jadi cache per-role di sini menghindari query "Has Role"
	# berulang untuk role yang sama dalam satu eksekusi.
	if role not in cache:
		cache[role] = frappe.get_all(
			HAS_ROLE_DOCTYPE, filters={"role": role, "parenttype": "User"}, pluck="parent"
		)
	return cache[role]


def _notify_pending_approver(quotation, workflow_state, role_users_cache):
	role = ROLE_BY_STATE.get(workflow_state)
	if not role:
		return

	users = _get_role_users(role, role_users_cache)
	if not users:
		return

	_safe_sendmail(
		users,
		frappe._("Eskalasi SLA: Quotation {0} belum di-approve >1x24 jam").format(quotation),
		frappe._(
			"Quotation {0} sudah lebih dari 1x24 jam menunggu approval pada tahap {1}. "
			"Mohon segera ditindaklanjuti."
		).format(quotation, workflow_state),
	)


def check_quotation_expiry():
	# PRD v8 Bagian 5.3/5.4 -- Quotation Approved yang melewati
	# tanggal_kadaluwarsa (45 hari sejak terbit, lihat quotation_hooks.py)
	# tanpa direspons client dipindah otomatis ke state "Kedaluwarsa".
	# Administrasi bisa mengaktifkannya kembali (action "Aktifkan Kembali")
	# tanpa perlu membuat Quotation baru dari nol -- lihat
	# quotation_hooks.py::_extend_expiry_on_reactivation.
	#
	# workflow_state di-set langsung lewat db_set (bypass Workflow engine),
	# bukan apply_workflow(), karena ini transisi otomatis oleh sistem
	# (scheduled job), bukan aksi user -- pola yang sama dipakai wo_hooks.py
	# untuk transisi otomatis lain. db_set melewati Version log, jadi
	# log_system_field_change menulis Version + Comment manual supaya tetap
	# ada jejak di timeline dokumen (lihat starlab_customizations/audit_log.py).
	quotations = frappe.get_all(
		"Quotation",
		filters={
			"workflow_state": "Approved",
			"tanggal_kadaluwarsa": ["<", nowdate()],
			"kedaluwarsa_notif_terkirim": 0,
			"docstatus": ["<", 2],
		},
		fields=["name"],
	)
	if not quotations:
		return

	users = frappe.get_all(
		HAS_ROLE_DOCTYPE, filters={"role": "Administrasi", "parenttype": "User"}, pluck="parent"
	)

	for row in quotations:
		frappe.db.set_value("Quotation", row.name, "workflow_state", "Kedaluwarsa")

		if users:
			_safe_sendmail(
				users,
				frappe._("Quotation {0} sudah kedaluwarsa").format(row.name),
				frappe._(
					"Quotation {0} sudah melewati tanggal kedaluwarsa dan belum direspons client."
					' Gunakan aksi "Aktifkan Kembali" bila ingin memperpanjang.'
				).format(row.name),
			)
		frappe.db.set_value("Quotation", row.name, "kedaluwarsa_notif_terkirim", 1)

		log_system_field_change(
			"Quotation",
			row.name,
			{
				"workflow_state": ("Approved", "Kedaluwarsa"),
				"kedaluwarsa_notif_terkirim": (0, 1),
			},
			frappe._(
				"Quotation ini otomatis dipindah ke status Kedaluwarsa oleh sistem karena melewati"
				' tanggal kedaluwarsa tanpa respons client. Gunakan aksi "Aktifkan Kembali" untuk'
				" memperpanjang tanpa membuat Quotation baru."
			),
		)


def _notify_role(role, subject, message, role_users_cache=None):
	users = (
		_get_role_users(role, role_users_cache)
		if role_users_cache is not None
		else frappe.get_all(HAS_ROLE_DOCTYPE, filters={"role": role, "parenttype": "User"}, pluck="parent")
	)
	if not users:
		return
	_safe_sendmail(users, subject, message)
	_notify_role_whatsapp(role, message)


def _notify_role_whatsapp(role, message):
	# TSD Bagian 10/11: WhatsApp adalah channel TAMBAHAN, bukan pengganti
	# email -- starlab_integrations bersifat opsional (belum tentu
	# terinstall/terkonfigurasi), jadi ini benar-benar no-op kalau app-nya
	# tidak ada atau WhatsApp Settings belum diisi (lihat whatsapp.py).
	try:
		frappe.get_attr("starlab_integrations.whatsapp._notify_role_via_whatsapp")(role, message)
	except Exception:
		pass


def check_invoice_due():
	# TSD Bagian 10: Sales Invoice due_date jatuh dalam H-3 dan
	# outstanding_amount > 0 -- reminder ke Finance & Administrasi.
	h3 = add_to_date(nowdate(), days=3, as_string=True)
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={
			"docstatus": 1,
			"due_date": ["between", [nowdate(), h3]],
			"outstanding_amount": [">", 0],
		},
		fields=["name", "due_date", "outstanding_amount"],
	)
	role_users_cache = {}
	for inv in invoices:
		message = frappe._("Invoice {0}: jatuh tempo {1}, outstanding {2}.").format(
			inv.name, inv.due_date, inv.outstanding_amount
		)
		subject = frappe._("Invoice jatuh tempo H-3: {0}").format(inv.name)
		_notify_role("Finance", subject, message, role_users_cache)
		_notify_role("Administrasi", subject, message, role_users_cache)


def check_invoice_overdue():
	# TSD Bagian 10: due_date < hari ini dan outstanding_amount > 0 --
	# eskalasi ke Finance & Direksi. ERPNext core sendiri sudah otomatis
	# menandai status "Overdue" (scheduled job update_invoice_status di
	# erpnext/hooks.py) -- ini menambahkan sisi notifikasinya saja.
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={
			"docstatus": 1,
			"due_date": ["<", nowdate()],
			"outstanding_amount": [">", 0],
		},
		fields=["name", "due_date", "outstanding_amount"],
	)
	role_users_cache = {}
	for inv in invoices:
		message = frappe._("Invoice {0}: sudah melewati jatuh tempo {1}, outstanding {2}.").format(
			inv.name, inv.due_date, inv.outstanding_amount
		)
		subject = frappe._("Invoice Overdue: {0}").format(inv.name)
		_notify_role("Finance", subject, message, role_users_cache)
		_notify_role("Direksi", subject, message, role_users_cache)
