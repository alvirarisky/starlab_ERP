import frappe
from frappe.model.naming import make_autoname
from frappe.utils import add_days, flt, getdate, nowdate

# Format dikonfirmasi dari dokumen Quotation asli SAI (Quo-SAI/V/2026/076,
# Quo-SAI/V/2026/075 -- lihat docs/dokumen asli/): "Quo-SAI/[bulan
# romawi]/[tahun]/[no urut 3 digit]". Nomor urut naik terus per TAHUN
# (bukan reset tiap bulan -- 075/076 sama-sama bulan Mei), jadi key seri
# di bawah sengaja hanya menyertakan tahun, bukan tahun+bulan.
ROMAN_MONTHS = {
	1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
	7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII",
}


def onload(doc, method=None):
	_populate_histori_lhu_klien(doc)


def _populate_histori_lhu_klien(doc):
	# Custom field histori_lhu_klien (Table, read_only -- lihat
	# custom_field.json) SENGAJA tidak disimpan sebagai data permanen di baris
	# Quotation ini; di-fetch ulang tiap form dibuka supaya selalu mencerminkan
	# LHU milik Customer yang sama secara live, termasuk LHU yang terbit
	# setelah Quotation ini dibuat.
	doc.set("histori_lhu_klien", [])
	if doc.quotation_to != "Customer" or not doc.party_name:
		return

	lhu_list = frappe.get_all(
		"LHU",
		filters={"customer": doc.party_name},
		fields=["name", "work_order", "tanggal_terbit", "status"],
		order_by="tanggal_terbit desc",
	)
	for row in lhu_list:
		doc.append(
			"histori_lhu_klien",
			{
				"lhu": row.name,
				"work_order": row.work_order,
				"tanggal_terbit": row.tanggal_terbit,
				"status": row.status,
			},
		)


def autoname(doc, method=None):
	date = getdate(doc.transaction_date or nowdate())
	roman = ROMAN_MONTHS[date.month]
	series_name = make_autoname(f"Quo-SAI-{date.year}-.###", doc.doctype)
	running_number = series_name.rsplit("-", 1)[-1]
	doc.name = f"Quo-SAI/{roman}/{date.year}/{running_number}"


EXPIRY_DAYS = 45


def validate(doc, method=None):
	for row in doc.get("parameter_detail") or []:
		row.harga_total = (row.frekuensi or 0) * (row.qty_per_titik or 0) * (row.harga_satuan or 0)

	# docstatus==0 guard: sebelumnya field ini dihitung ulang di setiap
	# validate() tanpa syarat, jadi kalau transaction_date pernah berubah
	# pasca-approval (docstatus 1) tanggal kadaluwarsa ikut bergeser diam-diam
	# meski Quotation-nya sudah Approved (audit temuan G.6).
	if doc.transaction_date and doc.docstatus == 0:
		doc.tanggal_kadaluwarsa = add_days(doc.transaction_date, EXPIRY_DAYS)

	_apply_tingkat_percepatan(doc)
	_set_active_tnc_template(doc)
	_calculate_price_summary(doc)
	_reset_sla_escalation_flag(doc)


TINGKAT_PERCEPATAN_TIER = {
	"7 Hari Kerja (+80%)": (7, 80),
	"5 Hari Kerja (+100%)": (5, 100),
}


def _apply_tingkat_percepatan(doc):
	# PRD v8 Sprint 12 / TSD Bab 4.6: dua tier rush fee terkonfirmasi PO.
	# rush_fee_hari/rush_fee_percent auto-fetch dari pilihan tingkat_percepatan;
	# untuk "Lainnya" tetap input manual (belum ada aturan baku tier lain --
	# lihat TODO di field-nya), dan "Normal" mengosongkan keduanya.
	tier = TINGKAT_PERCEPATAN_TIER.get(doc.tingkat_percepatan)
	if tier:
		doc.rush_fee_hari, doc.rush_fee_percent = tier
	elif doc.tingkat_percepatan == "Normal":
		doc.rush_fee_hari = 0
		doc.rush_fee_percent = 0
	# "Lainnya" -- biarkan rush_fee_hari/rush_fee_percent apa adanya (manual)


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


# PRD v8 Sprint 12, item 1: state approval yang approvernya (selain
# Administrasi di Draft) punya allow_edit sendiri -- kalau mereka mengubah
# konten quotation di state ini TANPA melalui aksi Tolak/Revisi, approval
# tahap sebelumnya (MT, dan MM untuk state Direksi) jadi tidak valid lagi
# karena mereview versi lama. "Revisi setelah sebagian disetujui" wajib
# mengulang rantai approval PENUH dari MT lagi -- bukan "lanjut dari titik
# terakhir" seperti asumsi lama.
STATES_AFTER_MT_APPROVAL = ["Menunggu Approval MM", "Menunggu Approval Direksi"]

NUMERIC_CONTENT_FIELDS = [
	"discount_percent", "biaya_kirim", "ppn_percent", "dp_percent",
	"rush_fee_hari", "rush_fee_percent",
]
TEXT_CONTENT_FIELDS = ["termin_pembayaran", "tingkat_percepatan"]


def _parameter_detail_signature(rows):
	return sorted(
		(row.parameter, flt(row.frekuensi), flt(row.qty_per_titik), flt(row.harga_satuan))
		for row in rows
	)


def _content_changed(doc, before):
	for field in NUMERIC_CONTENT_FIELDS:
		if flt(doc.get(field)) != flt(before.get(field)):
			return True
	for field in TEXT_CONTENT_FIELDS:
		if (doc.get(field) or "") != (before.get(field) or ""):
			return True
	return _parameter_detail_signature(doc.get("parameter_detail") or []) != _parameter_detail_signature(
		before.get("parameter_detail") or []
	)


def _revert_to_mt_if_content_changed_mid_approval(doc, before):
	if before.workflow_state not in STATES_AFTER_MT_APPROVAL:
		return False
	if before.workflow_state != doc.workflow_state:
		# Ini transisi resmi (Setujui/Tolak lewat Workflow engine), bukan
		# sekadar edit konten di tempat -- biarkan jalan normal.
		return False
	if not _content_changed(doc, before):
		return False

	# Bypass Workflow engine (frappe.model.workflow.validate_workflow tidak
	# mengizinkan lompat langsung dari MM/Direksi ke MT lewat field write
	# biasa, karena tidak ada transition edge untuk itu) -- pola yang sama
	# dipakai wo_hooks.py untuk transisi otomatis oleh sistem, bukan aksi
	# user langsung. db_set melewati Version log, jadi Comment manual
	# ditambahkan supaya tetap ada jejak di timeline dokumen.
	previous_state = before.workflow_state
	doc.db_set("workflow_state", "Menunggu Approval MT", notify=True)
	doc.db_set("workflow_state_since", frappe.utils.now_datetime())
	doc.db_set("eskalasi_terkirim", 0)
	doc.add_comment(
		"Info",
		frappe._(
			"Konten Quotation diubah saat berada di tahap {0} -- approval yang sudah didapat"
			" direset, wajib mengulang persetujuan penuh dari Manajer Teknis."
		).format(previous_state),
	)

	from starlab_customizations.tasks import _notify_role

	_notify_role(
		"Manajer Teknis",
		frappe._("Quotation {0} menunggu approval Anda (direvisi ulang)").format(doc.name),
		frappe._(
			"Quotation {0} diubah setelah sebagian disetujui, sehingga dikembalikan ke tahap"
			" approval Manajer Teknis."
		).format(doc.name),
	)
	return True


def _extend_expiry_on_reactivation(doc, before):
	# PRD v8 Sprint 12, item 2: aksi "Aktifkan Kembali" (Kedaluwarsa ->
	# Approved, lewat Workflow engine biasa karena ini aksi user/Administrasi
	# yang sah) memperpanjang tanggal_kadaluwarsa +45 hari dari tanggal
	# aktivasi ulang -- BUKAN dari transaction_date asli -- supaya Quotation
	# tidak perlu dibuat baru dari nol.
	if before.workflow_state != "Kedaluwarsa" or doc.workflow_state != "Approved":
		return

	doc.db_set("tanggal_kadaluwarsa", add_days(nowdate(), EXPIRY_DAYS))
	doc.db_set("kedaluwarsa_notif_terkirim", 0)
	doc.add_comment(
		"Info",
		frappe._(
			"Quotation diaktifkan kembali -- tanggal kedaluwarsa diperpanjang {0} hari dari hari ini."
		).format(EXPIRY_DAYS),
	)


def on_update(doc, method=None):
	before = doc.get_doc_before_save()
	if not before:
		return

	if _revert_to_mt_if_content_changed_mid_approval(doc, before):
		return

	_extend_expiry_on_reactivation(doc, before)

	# TSD Bagian 10 "Approval Pending": notifikasi SEGERA begitu Quotation
	# masuk ke state "Menunggu Approval [Role]" -- beda dari
	# check_quotation_sla di tasks.py yang baru mengingatkan setelah macet
	# >1x24 jam.
	if before.workflow_state == doc.workflow_state:
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
