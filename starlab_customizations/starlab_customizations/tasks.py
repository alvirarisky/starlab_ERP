import frappe
from frappe.utils import add_to_date, now_datetime, nowdate

PENDING_APPROVAL_STATES = [
	"Menunggu Approval MT",
	"Menunggu Approval MM",
	"Menunggu Approval Finance",
	"Menunggu Approval Marketing",
	"Menunggu Approval Direksi",
]

ROLE_BY_STATE = {
	"Menunggu Approval MT": "Manajer Teknis",
	"Menunggu Approval MM": "Manajer Mutu",
	"Menunggu Approval Finance": "Finance",
	"Menunggu Approval Marketing": "Marketing",
	"Menunggu Approval Direksi": "Direksi",
}


def check_quotation_sla():
	# PRD v6 SS5.5 -- eskalasi otomatis kalau approval Quotation macet >1x24 jam.
	#
	# TODO: target eskalasi (PRD v6 Open Question #1) belum dikonfirmasi PO --
	# opsinya "atasan approver", "langsung ke Direksi", atau "reminder ulang ke
	# approver yang sama". Default yang dipakai di sini SENGAJA yang paling
	# aman: reminder ulang ke approver yang sama pada state saat ini (role
	# lewat ROLE_BY_STATE) -- tidak menebak hierarki/atasan yang belum
	# terkonfirmasi, supaya notifikasi tidak salah kirim ke pihak yang keliru.
	# Ganti logika ini begitu PO memutuskan target eskalasi yang benar.
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
	for row in quotations:
		_notify_pending_approver(row.name, row.workflow_state)
		frappe.db.set_value("Quotation", row.name, "eskalasi_terkirim", 1)


def _notify_pending_approver(quotation, workflow_state):
	role = ROLE_BY_STATE.get(workflow_state)
	if not role:
		return

	users = frappe.get_all(
		"Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent"
	)
	if not users:
		return

	frappe.sendmail(
		recipients=users,
		subject=frappe._("Eskalasi SLA: Quotation {0} belum di-approve >1x24 jam").format(quotation),
		message=frappe._(
			"Quotation {0} sudah lebih dari 1x24 jam menunggu approval pada tahap {1}. "
			"Mohon segera ditindaklanjuti."
		).format(quotation, workflow_state),
	)


def check_quotation_expiry():
	# PRD v6 SS5.5 -- notifikasi ke Administrasi saat Quotation yang sudah
	# terbit ke client (Approved) melewati tanggal_kadaluwarsa (30 hari sejak
	# terbit) tanpa direspons. Belum menangani Open Question #6 (apakah bisa
	# di-extend) -- ini murni notifikasi, tidak mengubah status quotation.
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
		"Has Role", filters={"role": "Administrasi", "parenttype": "User"}, pluck="parent"
	)
	if not users:
		return

	for row in quotations:
		frappe.sendmail(
			recipients=users,
			subject=frappe._("Quotation {0} sudah kedaluwarsa").format(row.name),
			message=frappe._(
				"Quotation {0} sudah melewati tanggal kedaluwarsa dan belum direspons client."
			).format(row.name),
		)
		frappe.db.set_value("Quotation", row.name, "kedaluwarsa_notif_terkirim", 1)
