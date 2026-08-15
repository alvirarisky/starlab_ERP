import frappe
from frappe.utils import add_days, getdate, nowdate


def _safe_sendmail(recipients, subject, message):
	# frappe.sendmail raises OutgoingEmailError immediately when no default
	# outgoing Email Account is configured -- must never block the
	# scheduled job that triggered this notification.
	try:
		frappe.sendmail(recipients=recipients, subject=subject, message=message)
	except Exception:
		frappe.log_error(title="Gagal mengirim notifikasi email", message=frappe.get_traceback())


def _get_role_users(role, cache):
	# Cache per-role dalam satu eksekusi scheduled job -- menghindari query
	# "Has Role" berulang untuk role yang sama di setiap baris loop
	# (check_sample_deadline_mendekat/terlewat, check_sample_retensi).
	if role not in cache:
		cache[role] = frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent")
	return cache[role]


def _notify_role(role, subject, message, role_users_cache=None):
	users = (
		_get_role_users(role, role_users_cache)
		if role_users_cache is not None
		else frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent")
	)
	if not users:
		return
	_safe_sendmail(users, subject, message)


def check_sample_deadline_mendekat():
	# TSD Bagian 10: target_pengujian (WO Parameter Detail) jatuh dalam H-2 dan
	# status_pengujian belum "Done" -- reminder ke Laboratorium (PJ Analis
	# terkait) & Manajer Teknis. Dicek lewat WO Parameter Detail langsung
	# (child table punya field target_pengujian sendiri, bukan di parent WO).
	h2 = add_days(nowdate(), 2)
	rows = frappe.get_all(
		"WO Parameter Detail",
		filters={
			"target_pengujian": ["between", [nowdate(), h2]],
			"status_pengujian": ["!=", "Done"],
		},
		fields=["parent", "parameter", "pj_analis", "target_pengujian"],
	)
	if not rows:
		return

	# Batch-fetch Employee->user_id sekali untuk semua PJ Analis yang muncul,
	# alih-alih satu query get_value per baris.
	pj_analis_names = {row.pj_analis for row in rows if row.pj_analis}
	user_id_by_employee = (
		{
			e.name: e.user_id
			for e in frappe.get_all(
				"Employee", filters={"name": ["in", list(pj_analis_names)]}, fields=["name", "user_id"]
			)
		}
		if pj_analis_names
		else {}
	)
	role_users_cache = {}
	manajer_teknis_users = _get_role_users("Manajer Teknis", role_users_cache)

	for row in rows:
		users = list(manajer_teknis_users)
		user_id = user_id_by_employee.get(row.pj_analis)
		if user_id:
			users.append(user_id)
		if not users:
			continue
		_safe_sendmail(
			list(set(users)),
			frappe._("Deadline pengujian mendekat: {0}").format(row.parent),
			frappe._(
				"Work Order {0}, parameter {1}: target pengujian {2} sudah dalam H-2 dan belum selesai."
			).format(row.parent, row.parameter, row.target_pengujian),
		)


def check_sample_deadline_terlewat():
	# TSD Bagian 10: target_pengujian sudah lewat dan status_pengujian belum
	# "Done" -- eskalasi ke Manajer Teknis & Direksi.
	rows = frappe.get_all(
		"WO Parameter Detail",
		filters={
			"target_pengujian": ["<", nowdate()],
			"status_pengujian": ["!=", "Done"],
		},
		fields=["parent", "parameter", "target_pengujian"],
	)
	if not rows:
		return
	role_users_cache = {}
	for row in rows:
		_notify_role(
			"Manajer Teknis",
			frappe._("Deadline pengujian terlewat: {0}").format(row.parent),
			frappe._(
				"Work Order {0}, parameter {1}: target pengujian {2} sudah terlewat dan belum selesai."
			).format(row.parent, row.parameter, row.target_pengujian),
			role_users_cache,
		)
		_notify_role(
			"Direksi",
			frappe._("Eskalasi: deadline pengujian terlewat -- {0}").format(row.parent),
			frappe._(
				"Work Order {0}, parameter {1}: target pengujian {2} sudah terlewat dan belum selesai."
			).format(row.parent, row.parameter, row.target_pengujian),
			role_users_cache,
		)


def check_sample_retensi():
	# TSD Bagian 10: tanggal_musnah tercapai untuk Sample berstatus "Diarsipkan"
	# -- reminder ke Laboratorium & Manajer Teknis bahwa retensi sudah jatuh
	# tempo (siap diproses lewat transisi "Musnahkan").
	samples = frappe.get_all(
		"Sample",
		filters={"status": "Diarsipkan", "tanggal_musnah": ["<=", getdate(nowdate())]},
		fields=["name", "tanggal_musnah"],
	)
	if not samples:
		return
	role_users_cache = {}
	for sample in samples:
		message = frappe._(
			"Sample {0}: retensi sudah jatuh tempo sejak {1}, siap diproses pemusnahan."
		).format(sample.name, sample.tanggal_musnah)
		_notify_role(
			"Laboratorium",
			frappe._("Retensi Sample jatuh tempo: {0}").format(sample.name),
			message,
			role_users_cache,
		)
		_notify_role(
			"Manajer Teknis",
			frappe._("Retensi Sample jatuh tempo: {0}").format(sample.name),
			message,
			role_users_cache,
		)
