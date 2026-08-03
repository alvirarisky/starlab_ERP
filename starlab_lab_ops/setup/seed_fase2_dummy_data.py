import random
from datetime import datetime, timedelta

import frappe
from frappe.utils import add_days, nowdate

COMPANY = "Starlab Analitik Indonesia"
MATRIKS_LIST = ["Udara Ambien", "Udara Emisi", "Air Permukaan", "Air Bersih", "Air Limbah", "Tanah", "Sedimen", "Kebisingan"]

ANALIS = "Dewi Kusuma"
MM = "Siti Rahayu"
ADMIN = "Rina Marlina"
FINANCE = "Hendra Gunawan"


def _employee(full_name):
	first_name, *rest = full_name.split(" ", 1)
	last_name = rest[0] if rest else ""
	return frappe.db.get_value("Employee", {"first_name": first_name, "last_name": last_name, "company": COMPANY})


def seed_document_masters():
	if frappe.db.count("Document Master") >= 5:
		print("Document Master already seeded, skipping.")
		return
	docs = [
		("PM-SAI-01", "Panduan Mutu SAI", "PM - Panduan Mutu", "Edisi 3", "MM", "Aktif"),
		("PO-SAI-05", "Prosedur Pengujian Air Limbah", "PO - Prosedur Operasional", "Revisi 2", "MT", "Dalam Revisi"),
		("IKM-SAI-12", "Instruksi Kerja Metode Uji COD", "IKM - Instruksi Kerja Metode", "Revisi 1", "Laboratorium", "Aktif"),
		("DP-SAI-02", "Formulir Rekam Data Lapangan", "DP - Dokumen Pendukung", "Revisi 4", "Administrasi", "Usang"),
		("PO-SAI-08", "Prosedur Penanganan Sampel", "PO - Prosedur Operasional", "Revisi 1", "Laboratorium", "Aktif"),
	]
	for no, name, level, edisi, owner_div, status in docs:
		doc = frappe.get_doc({
			"doctype": "Document Master",
			"document_no": no,
			"document_name": name,
			"document_level": level,
			"edisi_revisi": edisi,
			"tanggal_efektif": add_days(nowdate(), -200),
			"owner_division": owner_div,
			# Document Master punya Frappe Workflow aktif (Draft -> ... -> Aktif
			# -> Dalam Revisi); insert langsung dengan status akhir kena tolak
			# WorkflowPermissionError karena bukan initial state. Insert selalu
			# sebagai Draft dulu (state awal yang valid), baru dipaksa ke status
			# akhir lewat db_set di bawah (bypass workflow -- wajar utk data
			# dummy historis yang "sudah lama begitu", bukan lagi diklik manual).
			"status": "Draft",
			"file_dokumen": "/files/placeholder_dokumen.pdf",
			"distribusi": [
				{"divisi": "Laboratorium", "tanggal_distribusi": add_days(nowdate(), -190), "acknowledged": 1, "acknowledged_on": add_days(nowdate(), -185)},
				{"divisi": "Administrasi", "tanggal_distribusi": add_days(nowdate(), -190), "acknowledged": 0},
				{"divisi": "MT", "tanggal_distribusi": add_days(nowdate(), -190), "acknowledged": 1, "acknowledged_on": add_days(nowdate(), -188)},
			],
		})
		doc.insert(ignore_permissions=True)
		if status != "Draft":
			doc.db_set("status", status, notify=False)
	print(f"Document Master: {frappe.db.count('Document Master')}")


def seed_work_orders():
	if frappe.db.count("Work Order Pengujian") >= 10:
		print("Work Order Pengujian already seeded, skipping.")
		return []

	customers = frappe.get_all("Customer", pluck="name")
	params = frappe.get_all("Test Parameter", fields=["name", "matriks"])
	statuses = ["Draft", "Approved", "In Progress", "Completed", "Cancelled"]
	kegiatan_list = [
		"Pengujian Kualitas Air Limbah", "Pengujian Udara Ambien", "Pengujian Emisi Cerobong",
		"Pengujian Air Bersih", "Pengujian Kebisingan Lingkungan Kerja", "Pengujian Tanah Terkontaminasi",
	]

	wo_names = []
	for i in range(10):
		wo_date = add_days(nowdate(), -(90 - i * 7))
		status = statuses[i % len(statuses)]
		rows = []
		n_rows = 2 + (i % 3)
		for j in range(n_rows):
			p = params[(i + j) % len(params)]
			rows.append({
				"matriks": p["matriks"],
				"parameter": p["name"],
				"sample_id_range": f"SMP-{i:02d}{j:02d}01 s/d SMP-{i:02d}{j:02d}03",
				"pj_analis": _employee(ANALIS),
				"target_pengujian": add_days(wo_date, 10),
				"status_pengujian": ["Pending", "In Progress", "Done", "Subkon"][(i + j) % 4],
			})
		doc = frappe.get_doc({
			"doctype": "Work Order Pengujian",
			"naming_series": "P.SAI.####.MM.YYYY",
			"customer": customers[i % len(customers)],
			"kegiatan": kegiatan_list[i % len(kegiatan_list)],
			"tanggal_wo": wo_date,
			# Work Order Pengujian punya Frappe Workflow aktif -- insert langsung
			# dengan status akhir kena WorkflowPermissionError (lihat catatan
			# sama di seed_document_masters). "Draft" adalah initial state-nya.
			"status": "Draft",
			"penerimaan_sampel": _employee(ADMIN),
			"wo_parameter_detail": rows,
		})
		doc.insert(ignore_permissions=True)
		if status != "Draft":
			doc.db_set("status", status, notify=False)
		wo_names.append(doc.name)
	print(f"Work Order Pengujian: {frappe.db.count('Work Order Pengujian')}")
	return wo_names


def seed_samples(wo_names):
	if frappe.db.count("Sample") >= 20:
		print("Sample already seeded, skipping.")
		return []
	if not wo_names:
		wo_names = frappe.get_all("Work Order Pengujian", pluck="name")

	statuses = ["Diterima", "Sedang Diuji", "Divalidasi", "Diarsipkan", "Dimusnahkan"]
	sample_names = []
	for i in range(20):
		wo = wo_names[i % len(wo_names)]
		wo_doc_date = frappe.db.get_value("Work Order Pengujian", wo, "tanggal_wo")
		status = statuses[i % len(statuses)]
		is_disposable = status == "Dimusnahkan" or i % 4 == 3
		retensi = "Bisa Dibuang" if is_disposable else "Tahan"
		tanggal_musnah = add_days(nowdate(), -(10 + i)) if is_disposable else None
		sample_id = f"SMP-{i + 1:04d}"
		doc = frappe.get_doc({
			"doctype": "Sample",
			"sample_id": sample_id,
			"work_order": wo,
			"matriks": MATRIKS_LIST[i % len(MATRIKS_LIST)],
			"tanggal_terima": add_days(wo_doc_date, 1),
			# Sample juga punya Frappe Workflow aktif; "Diterima" adalah
			# initial state-nya (bukan status akhir yang mau di-seed).
			"status": "Diterima",
			"retensi": retensi,
			"tanggal_musnah": tanggal_musnah,
		})
		doc.insert(ignore_permissions=True)
		if status != "Diterima":
			doc.db_set("status", status, notify=False)
		sample_names.append(doc.name)
	print(f"Sample: {frappe.db.count('Sample')}")
	return sample_names


def seed_test_results(sample_names):
	if frappe.db.count("Test Result") >= 30:
		print("Test Result already seeded, skipping.")
		return
	if not sample_names:
		sample_names = frappe.get_all("Sample", pluck="name")

	params = frappe.get_all("Test Parameter", fields=["name", "satuan"])
	statuses = ["Draft", "Diajukan Validasi", "Divalidasi", "Ditolak"]

	for i in range(30):
		sample = sample_names[i % len(sample_names)]
		param = params[i % len(params)]
		status = statuses[i % len(statuses)]
		qc_rows = []
		if i % 3 == 0:
			qc_rows.append({
				"qc_type": ["Kurva Kalibrasi", "Ripitabilitas", "Trueness"][i % 3],
				"nilai_slope": round(random.uniform(0.9, 1.1), 4),
				"nilai_intersep": round(random.uniform(-0.05, 0.05), 4),
				"nilai_r2": round(random.uniform(0.98, 0.999), 4),
				"nilai_rpd_persen": round(random.uniform(1, 15), 2),
				"nilai_trueness_persen": round(random.uniform(85, 110), 2),
			})
		doc = frappe.get_doc({
			"doctype": "Test Result",
			"sample": sample,
			"work_order": frappe.db.get_value("Sample", sample, "work_order"),
			"parameter": param["name"],
			"analis": _employee(ANALIS),
			"hasil_uji": round(random.uniform(0.5, 200), 2),
			"satuan": param["satuan"],
			"qc_detail": qc_rows,
			# Test Result juga punya Frappe Workflow aktif; "Draft" adalah
			# initial state-nya.
			"status": "Draft",
		})
		if status in ("Divalidasi", "Ditolak"):
			doc.validated_by = _employee(MM)
			doc.validated_on = datetime.now() - timedelta(days=i)
			if status == "Ditolak":
				doc.catatan_validasi = "Hasil di luar rentang QC, perlu uji ulang."
		doc.insert(ignore_permissions=True)
		if status != "Draft":
			doc.db_set("status", status, notify=False)
	print(f"Test Result: {frappe.db.count('Test Result')}")


def seed_lhu(wo_names):
	if frappe.db.count("LHU") >= 5:
		print("LHU already seeded, skipping.")
		return
	if not wo_names:
		wo_names = frappe.get_all("Work Order Pengujian", pluck="name")

	for i, wo in enumerate(wo_names[:5]):
		wo_customer = frappe.db.get_value("Work Order Pengujian", wo, "customer")
		samples = frappe.get_all("Sample", filters={"work_order": wo}, pluck="name")
		test_results = frappe.get_all(
			"Test Result", filters={"sample": ["in", samples]},
			fields=["name", "parameter", "hasil_uji", "satuan"], limit_page_length=5,
		)
		rows = []
		for tr in test_results:
			regulasi = frappe.db.get_value("Test Parameter", tr["parameter"], "regulasi_acuan")
			rows.append({
				"test_result": tr["name"],
				"parameter": tr["parameter"],
				"hasil_uji": tr["hasil_uji"],
				"satuan": tr["satuan"],
				"metode_acuan": regulasi,
			})
		if not rows:
			continue
		doc = frappe.get_doc({
			"doctype": "LHU",
			"naming_series": "LHU-####-MM-YYYY",
			"work_order": wo,
			"customer": wo_customer,
			"tanggal_terbit": add_days(nowdate(), -(5 + i)),
			"diterbitkan_oleh": _employee(ADMIN),
			"test_result_list": rows,
			"status": "Issued",
		})
		doc.insert(ignore_permissions=True)
	print(f"LHU: {frappe.db.count('LHU')}")


def seed_petty_cash_and_journal_entries():
	if frappe.db.count("Petty Cash Entry") >= 5:
		print("Petty Cash Entry already seeded, skipping.")
	else:
		items = [
			("Beli Alat Tulis Kantor", 150000, "Draft"),
			("Bensin Kendaraan Operasional", 300000, "Menunggu Approval"),
			("Konsumsi Rapat Internal", 250000, "Disetujui"),
			("Token Listrik Laboratorium", 500000, "Disetujui"),
			("Cetak Dokumen LHU", 100000, "Ditolak"),
		]
		for i, (item, nominal, status) in enumerate(items):
			doc = frappe.get_doc({
				"doctype": "Petty Cash Entry",
				"tanggal": add_days(nowdate(), -(20 - i * 3)),
				"item": item,
				"nominal": nominal,
				"bukti": "/files/placeholder_bukti.jpg",
				"keterangan": f"Pengeluaran operasional harian - {item}",
				# Petty Cash Entry juga punya Frappe Workflow aktif; "Draft"
				# adalah initial state-nya. db_set di bawah bypass workflow
				# SEKALIGUS tidak memicu on_update_petty_cash_entry (db_set
				# tidak menjalankan hook doc_events) -- ini yang diharapkan
				# utk data seed histori, bukan simulasi klik approve
				# sungguhan (itu ditest manual di Langkah verifikasi akhir).
				"status": "Draft",
				"disetujui_oleh": _employee(FINANCE) if status == "Disetujui" else None,
			})
			doc.insert(ignore_permissions=True)
			if status != "Draft":
				doc.db_set("status", status, notify=False)
		print(f"Petty Cash Entry: {frappe.db.count('Petty Cash Entry')}")

	if frappe.db.count("Journal Entry", filters={"user_remark": ["like", "%SAI dummy%"]}) >= 2:
		print("Journal Entry (dummy) already seeded, skipping.")
		return
	# 2026-08-03: nama akun disamakan dengan COA default ERPNext yang beneran
	# ter-generate di Company instance ini (bukan template Indonesia berkode
	# angka yang diasumsikan sebelumnya -- lihat catatan di petty_cash_hooks.py).
	expense_account = "Bank Charges - SAI"
	cash_account = "Cash - SAI"
	for i in range(2):
		je = frappe.get_doc({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": COMPANY,
			"posting_date": add_days(nowdate(), -(15 - i * 5)),
			"set_posting_time": 1,
			"user_remark": "Entry manual pembanding - SAI dummy",
			"accounts": [
				{"account": expense_account, "debit_in_account_currency": 200000 + i * 50000, "credit_in_account_currency": 0},
				{"account": cash_account, "debit_in_account_currency": 0, "credit_in_account_currency": 200000 + i * 50000},
			],
		})
		je.insert(ignore_permissions=True)
		je.submit()
	print("Journal Entry dummy pembanding: 2 created.")


def seed_sales_invoices():
	if frappe.db.count("Sales Invoice", filters={"remarks": ["like", "%SAI dummy%"]}) >= 5:
		print("Sales Invoice already seeded, skipping.")
		return
	customers = frappe.get_all("Customer", pluck="name")
	due_offsets = [-20, -5, 3, 20, 45]  # overdue, overdue, dekat, belum jatuh tempo, belum jatuh tempo
	for i, offset in enumerate(due_offsets):
		posting_date = add_days(nowdate(), -30)
		si = frappe.get_doc({
			"doctype": "Sales Invoice",
			"customer": customers[i % len(customers)],
			"company": COMPANY,
			"posting_date": posting_date,
			"set_posting_time": 1,
			"due_date": add_days(nowdate(), offset),
			"remarks": "Invoice dummy testing Aging Piutang - SAI dummy",
			"items": [{
				"item_code": "REG-001",
				"qty": 1,
				"rate": 500000 + i * 50000,
				"cost_center": "Main - SAI",
				"income_account": "Sales - SAI",
			}],
		})
		si.insert(ignore_permissions=True)
		si.submit()
	print("Sales Invoice dummy: 5 created & submitted.")


def seed_bank_reconciliation_data():
	if not frappe.db.exists("Bank", "Bank BCA"):
		frappe.get_doc({"doctype": "Bank", "bank_name": "Bank BCA"}).insert(ignore_permissions=True)
		frappe.db.commit()

	bank_account_ledger = frappe.db.get_value("Account", {"account_name": "Bank BCA", "company": COMPANY})
	if not bank_account_ledger:
		acc = frappe.get_doc({
			"doctype": "Account",
			"account_name": "Bank BCA",
			"parent_account": "Bank Accounts - SAI",
			"account_type": "Bank",
			"company": COMPANY,
			"account_currency": "IDR",
		})
		acc.insert(ignore_permissions=True)
		bank_account_ledger = acc.name
		frappe.db.commit()

	bank_account_name = frappe.db.get_value("Bank Account", {"account_name": "BCA", "bank": "Bank BCA"})
	if not bank_account_name:
		ba = frappe.get_doc({
			"doctype": "Bank Account",
			"account_name": "BCA",
			"bank": "Bank BCA",
			"account": bank_account_ledger,
			"company": COMPANY,
			"is_company_account": 1,
		})
		ba.insert(ignore_permissions=True)
		bank_account_name = ba.name
		frappe.db.commit()

	customers = frappe.get_all("Customer", pluck="name")

	# Unmatched deposit
	if not frappe.db.exists("Bank Transaction", {"description": "Transfer masuk belum dicocokkan - dummy"}):
		bt1 = frappe.get_doc({
			"doctype": "Bank Transaction",
			"date": add_days(nowdate(), -10),
			"set_posting_time": 1,
			"bank_account": bank_account_name,
			"deposit": 750000,
			"withdrawal": 0,
			"currency": "IDR",
			"description": "Transfer masuk belum dicocokkan - dummy",
		})
		bt1.insert(ignore_permissions=True)
		bt1.submit()
		frappe.db.commit()

	# Matched deposit: create a standalone Payment Entry (advance receive) then link
	pe_name = frappe.db.get_value("Payment Entry", {"remarks": ["like", "%SAI dummy reconciled%"]})
	if not pe_name:
		pe = frappe.get_doc({
			"doctype": "Payment Entry",
			"payment_type": "Receive",
			"party_type": "Customer",
			"party": customers[0],
			"company": COMPANY,
			"posting_date": add_days(nowdate(), -8),
			"set_posting_time": 1,
			"remarks": "SAI dummy reconciled",
			"reference_no": "TF-DUMMY-001",
			"reference_date": add_days(nowdate(), -8),
			"paid_from": frappe.db.get_value("Company", COMPANY, "default_receivable_account"),
			"paid_to": bank_account_ledger,
			"paid_amount": 1000000,
			"received_amount": 1000000,
		})
		pe.insert(ignore_permissions=True)
		pe.submit()
		pe_name = pe.name
		frappe.db.commit()

	if not frappe.db.exists("Bank Transaction", {"description": "Transfer masuk sudah dicocokkan - dummy"}):
		bt2 = frappe.get_doc({
			"doctype": "Bank Transaction",
			"date": add_days(nowdate(), -8),
			"set_posting_time": 1,
			"bank_account": bank_account_name,
			"deposit": 1000000,
			"withdrawal": 0,
			"currency": "IDR",
			"description": "Transfer masuk sudah dicocokkan - dummy",
			"payment_entries": [{
				"payment_document": "Payment Entry",
				"payment_entry": pe_name,
				"allocated_amount": 1000000,
			}],
		})
		bt2.insert(ignore_permissions=True)
		bt2.submit()
		frappe.db.commit()
	print("Bank Transaction + Payment Entry dummy: done.")


def seed_critical_stock():
	targets = [("REG-001", 2), ("REG-003", 5)]
	for item_code, target_qty in targets:
		current_qty = frappe.db.get_value(
			"Bin", {"item_code": item_code, "warehouse": "Stores - SAI"}, "actual_qty"
		) or 0
		if current_qty == target_qty:
			continue
		sr = frappe.get_doc({
			"doctype": "Stock Reconciliation",
			"company": COMPANY,
			"purpose": "Stock Reconciliation",
			# 2026-08-03: item-item ini belum pernah punya Stock Ledger Entry
			# sama sekali, jadi ERPNext otomatis memperlakukan reconciliation
			# ini sebagai "Opening Entry" dan MEWAJIBKAN Difference Account
			# bertipe Asset/Liability (menolak akun Expense seperti "Stock
			# Adjustment - SAI" yang dipakai sebelumnya, lihat
			# OpeningEntryAccountError). "Temporary Opening" adalah akun
			# Asset bawaan ERPNext yang memang dipakai khusus utk kasus ini.
			"expense_account": "Temporary Opening - SAI",
			"items": [{
				"item_code": item_code,
				"warehouse": "Stores - SAI",
				"qty": target_qty,
				"valuation_rate": 50000,
			}],
		})
		sr.insert(ignore_permissions=True)
		sr.submit()
	print("Stock Reconciliation untuk stok kritis: done.")


def execute():
	seed_document_masters()
	frappe.db.commit()
	wo_names = seed_work_orders()
	frappe.db.commit()
	sample_names = seed_samples(wo_names)
	frappe.db.commit()
	seed_test_results(sample_names)
	frappe.db.commit()
	seed_lhu(wo_names)
	frappe.db.commit()
	seed_petty_cash_and_journal_entries()
	frappe.db.commit()
	seed_sales_invoices()
	frappe.db.commit()
	seed_bank_reconciliation_data()
	frappe.db.commit()
	seed_critical_stock()
	frappe.db.commit()
	print("Fase 2 dummy data seeding done.")
