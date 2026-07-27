import frappe
from frappe.rate_limiter import rate_limit

# PRD v8 Bagian 5.7 / TSD Bab 11: Client Dashboard read-only berbasis nomor
# pesanan (Quotation atau Work Order Pengujian) TANPA login. Endpoint ini
# SENGAJA tidak pernah mengembalikan data harga/finansial apa pun -- cuma
# status pekerjaan + tautan unduh LHU -- supaya dampaknya tetap terbatas
# kalau nomor pesanan bocor ke pihak yang tidak berkepentingan. Mitigasi
# risiko penebakan nomor pesanan dilakukan lewat rate-limiting di bawah,
# bukan lewat autentikasi tambahan (sesuai keputusan Product Owner).


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=30, seconds=60)
def track_order(nomor_pesanan: str):
	nomor_pesanan = (nomor_pesanan or "").strip()
	if not nomor_pesanan:
		frappe.throw(frappe._("Nomor pesanan wajib diisi"))

	if frappe.db.exists("Work Order Pengujian", nomor_pesanan):
		return {
			"found": True,
			"nomor_pesanan": nomor_pesanan,
			"pekerjaan": [_work_order_summary(nomor_pesanan)],
		}

	if frappe.db.exists("Quotation", nomor_pesanan):
		work_orders = frappe.get_all(
			"Work Order Pengujian", filters={"quotation": nomor_pesanan}, pluck="name"
		)
		if work_orders:
			return {
				"found": True,
				"nomor_pesanan": nomor_pesanan,
				"pekerjaan": [_work_order_summary(wo) for wo in work_orders],
			}

		workflow_state = frappe.db.get_value("Quotation", nomor_pesanan, "workflow_state")
		return {
			"found": True,
			"nomor_pesanan": nomor_pesanan,
			"status_pekerjaan": _friendly_quotation_status(workflow_state),
			"pekerjaan": [],
		}

	return {"found": False}


def _work_order_summary(work_order_name):
	wo = frappe.db.get_value(
		"Work Order Pengujian", work_order_name, ["name", "status", "tanggal_wo"], as_dict=True
	)
	lhu_list = frappe.get_all(
		"LHU",
		filters={"work_order": work_order_name},
		fields=["name", "status", "tanggal_terbit", "file_lhu"],
		order_by="tanggal_terbit desc",
	)
	return {
		"work_order": wo.name,
		"status_pekerjaan": wo.status,
		"tanggal_wo": wo.tanggal_wo,
		"lhu": [
			{
				"name": lhu.name,
				"status": lhu.status,
				"tanggal_terbit": lhu.tanggal_terbit,
				"file_lhu": lhu.file_lhu or None,
			}
			for lhu in lhu_list
		],
	}


def _friendly_quotation_status(workflow_state):
	# Quotation yang belum punya Work Order sama sekali -- kemungkinan masih
	# di tahap approval internal atau menunggu respons client. Sengaja tidak
	# menyebut nama tahap approval (mis. "Menunggu Approval MT") ke client,
	# itu detail internal yang tidak relevan bagi mereka.
	if not workflow_state:
		return "Diterima"
	if workflow_state == "Approved":
		return "Disetujui -- menunggu penjadwalan pengujian"
	if workflow_state == "Rejected":
		return "Ditolak"
	if workflow_state == "Cancelled":
		return "Dibatalkan"
	return "Sedang diproses secara internal"
