import frappe


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
	for row in test_results:
		# metode_acuan idealnya fetch dari Test Parameter.regulasi_acuan lewat
		# Test Result.parameter (2 level), tapi fetch_from Frappe cuma dukung
		# 1 level -- diisi manual di sini (TODO lama dari setup script Fase 2
		# akhirnya diselesaikan di titik ini, bukan lewat Server Script terpisah).
		metode_acuan = frappe.db.get_value("Test Parameter", row.parameter, "regulasi_acuan")
		doc.append(
			"test_result_list",
			{
				"test_result": row.name,
				"metode_acuan": metode_acuan,
			},
		)
