import frappe
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification

# owner_division / Document Distribution.divisi use short codes (Sprint 1
# schema); everywhere else in this project "division" access control is
# expressed as a Frappe Role. This maps one to the other so Workflow
# conditions and permission checks can key off the Roles already assigned
# to Users instead of introducing a separate Division doctype.
ROLE_BY_DIVISION_CODE = {
	"Direksi": "Direksi",
	"MM": "Manajer Mutu",
	"MT": "Manajer Teknis",
	"Laboratorium": "Laboratorium",
	"Administrasi": "Administrasi",
	"Finance": "Finance",
	"Marketing": "Marketing",
}


def _notify_role(role, subject, message):
	users = frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent")
	if not users:
		return
	# frappe.sendmail raises OutgoingEmailError immediately when no default
	# outgoing Email Account is configured -- must never block the workflow
	# transition that triggered this notification.
	try:
		frappe.sendmail(recipients=users, subject=subject, message=message)
	except Exception:
		frappe.log_error(title="Gagal mengirim notifikasi email", message=frappe.get_traceback())


def validate_document_master(doc, method=None):
	before = doc.get_doc_before_save()
	if not before or before.status == doc.status:
		return

	if before.status in ("Menunggu Approval MM", "Menunggu Approval Direksi") and doc.status == "Draft":
		if not doc.catatan_revisi:
			frappe.throw(frappe._("Catatan Revisi wajib diisi saat menolak/mengembalikan dokumen ke Draft"))


def on_update_document_master(doc, method=None):
	before = doc.get_doc_before_save()
	if not before or before.status == doc.status:
		return

	# TSD Bagian 10 "Approval Pending": notifikasi segera begitu dokumen masuk
	# ke tahap approval-nya masing-masing.
	approval_role = {"Menunggu Approval MM": "Manajer Mutu", "Menunggu Approval Direksi": "Direksi"}.get(doc.status)
	if approval_role:
		_notify_role(
			approval_role,
			frappe._("Dokumen {0} menunggu approval Anda").format(doc.name),
			frappe._("Dokumen {0} ({1}) menunggu approval Anda.").format(doc.name, doc.document_name),
		)

	if doc.status == "Aktif" and before.status == "Menunggu Approval Direksi":
		_append_revision_log(doc, before)
		_notify_distribution(doc)


def _append_revision_log(doc, before):
	# Document Revision terisi otomatis (bukan diisi manual) -- lihat TSD SS4.6
	# ("child, read-only, terisi otomatis tiap kali edisi/revisi berubah").
	# Insert langsung sebagai child row, bukan doc.append + doc.save(), supaya
	# tidak memicu ulang on_update ini (before.status == doc.status baru akan
	# match setelah row ini masuk, jadi re-entry aman, tapi lebih murah untuk
	# tidak menjalankan ulang seluruh validate() Document Master).
	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	next_idx = len(doc.get("revisi_history") or []) + 1
	frappe.get_doc(
		{
			"doctype": "Document Revision",
			"parent": doc.name,
			"parenttype": "Document Master",
			"parentfield": "revisi_history",
			"idx": next_idx,
			"revisi_ke": doc.edisi_revisi,
			"tanggal_revisi": frappe.utils.nowdate(),
			"diubah_oleh": employee,
			"ringkasan_perubahan": doc.catatan_revisi,
			"file_versi_lama": before.file_dokumen,
		}
	).insert(ignore_permissions=True)
	if doc.catatan_revisi:
		doc.db_set("catatan_revisi", "", notify=False)


def _notify_distribution(doc):
	roles = {ROLE_BY_DIVISION_CODE.get(row.divisi) for row in (doc.get("distribusi") or [])}
	roles.discard(None)
	if not roles:
		return

	users = set()
	for role in roles:
		users.update(frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent"))
	users.discard("Administrator")
	users.discard("Guest")
	if not users:
		return

	try:
		enqueue_create_notification(
			list(users),
			{
				"type": "Alert",
				"document_type": "Document Master",
				"document_name": doc.name,
				"subject": frappe._("Dokumen {0} ({1}) sudah Aktif -- edisi/revisi terbaru berlaku.").format(
					doc.name, doc.document_name
				),
				"from_user": frappe.session.user,
			},
		)
	except Exception:
		frappe.log_error(
			title="Notifikasi distribusi Document Master gagal",
			message=frappe.get_traceback(),
		)


def has_permission(doc, ptype=None, user=None):
	user = user or frappe.session.user
	roles = frappe.get_roles(user)
	if "Manajer Mutu" in roles or "System Manager" in roles:
		return True

	owner_role = ROLE_BY_DIVISION_CODE.get(doc.owner_division)

	if ptype and ptype != "read":
		if "Direksi" in roles:
			# Direksi butuh write untuk menjalankan transisi Terbitkan/Tolak,
			# bukan untuk mengedit dokumen milik divisi lain secara bebas.
			return True
		if "Manajer Teknis" in roles:
			# Manajer Teknis hanya boleh mengubah dokumen level IKM yang jadi
			# tanggung jawab divisinya sendiri (TSD SS7.8).
			return doc.document_level == "IKM - Instruksi Kerja Metode" and doc.owner_division == "MT"
		# Divisi lain (Marketing/Administrasi/Finance/Laboratorium) hanya
		# boleh membuat/mengubah dokumen milik divisinya sendiri -- ini
		# perluasan dari tabel SS7.8 supaya transisi "Ajukan" oleh "divisi
		# pemilik dokumen" (SS6.5) bisa berfungsi, lihat description DocType.
		return owner_role in roles

	if "Direksi" in roles:
		return True

	distributed_codes = {row.divisi for row in (doc.get("distribusi") or [])}
	distributed_roles = {ROLE_BY_DIVISION_CODE.get(code) for code in distributed_codes}
	distributed_roles.discard(None)
	return bool(distributed_roles & set(roles)) or owner_role in roles


def get_permission_query_conditions(user=None):
	user = user or frappe.session.user
	roles = frappe.get_roles(user)
	if "Manajer Mutu" in roles or "Direksi" in roles or "System Manager" in roles:
		return ""

	my_codes = [code for code, role in ROLE_BY_DIVISION_CODE.items() if role in roles]
	if not my_codes:
		return "1=0"

	codes_sql = ", ".join(frappe.db.escape(code) for code in my_codes)
	return f"""(
		`tabDocument Master`.owner_division in ({codes_sql})
		or exists (
			select 1 from `tabDocument Distribution` dd
			where dd.parent = `tabDocument Master`.name and dd.divisi in ({codes_sql})
		)
	)"""
