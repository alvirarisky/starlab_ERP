import frappe

MODULE = "Starlab Lab Ops"


def _create_if_missing(doctype_dict):
	name = doctype_dict["name"]
	if frappe.db.exists("DocType", name):
		print(f"{name} already exists, skipping.")
		return
	frappe.get_doc(doctype_dict).insert()
	print(f"{name} created.")


def create_lhu_test_result_detail():
	_create_if_missing({
		"doctype": "DocType",
		"name": "LHU Test Result Detail",
		"module": MODULE,
		"custom": 0,
		"istable": 1,
		"editable_grid": 1,
		"fields": [
			{"fieldname": "test_result", "label": "Test Result", "fieldtype": "Link", "options": "Test Result", "in_list_view": 1},
			{"fieldname": "parameter", "label": "Parameter", "fieldtype": "Data", "read_only": 1, "fetch_from": "test_result.parameter", "in_list_view": 1},
			{"fieldname": "hasil_uji", "label": "Hasil Uji", "fieldtype": "Float", "read_only": 1, "fetch_from": "test_result.hasil_uji", "in_list_view": 1},
			{"fieldname": "satuan", "label": "Satuan", "fieldtype": "Data", "read_only": 1, "fetch_from": "test_result.satuan", "in_list_view": 1},
			# NOTE: metode_acuan idealnya fetch dari Test Parameter.regulasi_acuan lewat
			# Test Result.parameter (2 level), tapi fetch_from Frappe cuma dukung 1 level
			# dotted traversal. Untuk stub ini dibiarkan read-only tanpa auto-fetch;
			# diisi manual/lewat script. TODO(sprint resmi): auto-fetch via Server Script.
			{"fieldname": "metode_acuan", "label": "Metode Acuan", "fieldtype": "Data", "read_only": 1, "in_list_view": 1},
		],
	})


def create_lhu():
	_create_if_missing({
		"doctype": "DocType",
		"name": "LHU",
		"module": MODULE,
		"custom": 0,
		"autoname": "naming_series:",
		"naming_rule": "By \"Naming Series\" field",
		"track_changes": 1,
		"sort_field": "modified",
		"sort_order": "DESC",
		"fields": [
			{"fieldname": "naming_series", "label": "Naming Series", "fieldtype": "Select", "options": "LHU-####-MM-YYYY", "reqd": 1},
			{"fieldname": "work_order", "label": "Work Order", "fieldtype": "Link", "options": "Work Order Pengujian", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "reqd": 1,
			 "fetch_from": "work_order.customer", "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "tanggal_terbit", "label": "Tanggal Terbit", "fieldtype": "Date", "reqd": 1, "in_list_view": 1},
			{"fieldname": "diterbitkan_oleh", "label": "Diterbitkan Oleh", "fieldtype": "Link", "options": "Employee", "reqd": 1},
			{"fieldname": "test_result_list", "label": "Daftar Hasil Uji", "fieldtype": "Table", "options": "LHU Test Result Detail", "reqd": 1},
			{"fieldname": "status", "label": "Status", "fieldtype": "Select",
			 "options": "Draft\nIssued\nRevised\nSuperseded", "reqd": 1, "default": "Draft",
			 "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "file_lhu", "label": "File LHU", "fieldtype": "Attach"},
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1, "email": 1, "share": 1},
		],
	})


def execute():
	create_lhu_test_result_detail()
	create_lhu()
	frappe.db.commit()
	print("LHU + LHU Test Result Detail done.")
