import frappe
from frappe.utils import add_days, flt

# TODO: format auto-numbering Quotation belum sesuai SAI, lihat PRD v6 Open
# Question #5 -- naming saat ini masih naming series default bawaan ERPNext
# (bukan format Quo-SAI/[bulan romawi]/[tahun]/[no urut] dari BRA/PRD).
# Jangan hardcode asumsi format final apa pun sebelum dikonfirmasi Administrasi.


def validate(doc, method=None):
	for row in doc.get("parameter_detail") or []:
		row.harga_total = (row.frekuensi or 0) * (row.qty_per_titik or 0) * (row.harga_satuan or 0)

	# docstatus==0 guard: sebelumnya field ini dihitung ulang di setiap
	# validate() tanpa syarat, jadi kalau transaction_date pernah berubah
	# pasca-approval (docstatus 1) tanggal kadaluwarsa ikut bergeser diam-diam
	# meski Quotation-nya sudah Approved (audit temuan G.6).
	if doc.transaction_date and doc.docstatus == 0:
		doc.tanggal_kadaluwarsa = add_days(doc.transaction_date, 30)

	_set_active_tnc_template(doc)
	_calculate_price_summary(doc)
	_reset_sla_escalation_flag(doc)


def _set_active_tnc_template(doc):
	# Auto-pilih TNC Master Template yang berlaku sekali di awal (saat dibuat),
	# lalu dikunci -- Quotation yang sudah terbit tetap merujuk versi T&C yang
	# berlaku saat itu, bukan selalu versi terbaru (PRD v6 SS5.3).
	if doc.tnc_template or not doc.is_new():
		return

	latest = frappe.get_all(
		"TNC Master Template",
		filters={"berlaku_sejak": ["<=", doc.transaction_date or frappe.utils.nowdate()]},
		order_by="berlaku_sejak desc, creation desc",
		limit=1,
		pluck="name",
	)
	if latest:
		doc.tnc_template = latest[0]


def _calculate_price_summary(doc):
	# Urutan ringkasan harga mengikuti PRD v6 SS5.3: Sub Total -> Discount (%)
	# -> DPP -> PPN (%) -> Biaya Kirim -> Total Invoice. Rush fee (rush_fee_hari/
	# rush_fee_percent) sengaja TIDAK diikutkan ke kalkulasi ini -- lihat TODO
	# di field-nya (PRD v6 Open Question #10 belum dikonfirmasi).
	doc.sub_total = sum(flt(row.harga_total) for row in (doc.get("parameter_detail") or []))
	doc.dpp = doc.sub_total - (doc.sub_total * flt(doc.discount_percent) / 100)
	doc.total_invoice = doc.dpp + (doc.dpp * flt(doc.ppn_percent) / 100) + flt(doc.biaya_kirim)


def _reset_sla_escalation_flag(doc):
	# eskalasi_terkirim menandai "sudah pernah diingatkan" untuk state
	# approval saat ini (lihat starlab_customizations/tasks.py). Setiap kali
	# workflow_state berubah (approve/reject/revisi), reset supaya state
	# berikutnya bisa dapat pengingatnya sendiri kalau ikut macet >1x24 jam.
	before = doc.get_doc_before_save()
	if before and before.workflow_state != doc.workflow_state:
		doc.eskalasi_terkirim = 0


def on_update(doc, method=None):
	# TSD Bagian 10 "Approval Pending": notifikasi SEGERA begitu Quotation
	# masuk ke state "Menunggu Approval [Role]" -- beda dari
	# check_quotation_sla di tasks.py yang baru mengingatkan setelah macet
	# >1x24 jam.
	before = doc.get_doc_before_save()
	if not before or before.workflow_state == doc.workflow_state:
		return

	from starlab_customizations.tasks import ROLE_BY_STATE, _notify_role

	role = ROLE_BY_STATE.get(doc.workflow_state)
	if not role:
		return

	_notify_role(
		role,
		frappe._("Quotation {0} menunggu approval Anda").format(doc.name),
		frappe._("Quotation {0} sudah masuk ke tahap approval Anda ({1}).").format(doc.name, doc.workflow_state),
	)
