import frappe

MODULE = "Starlab Lab Ops"


def _create_if_missing(doctype_dict):
	name = doctype_dict["name"]
	if frappe.db.exists("DocType", name):
		print(f"{name} already exists, skipping.")
		return
	frappe.get_doc(doctype_dict).insert()
	print(f"{name} created.")


def create_qc_detail():
	_create_if_missing({
		"doctype": "DocType",
		"name": "QC Detail",
		"module": MODULE,
		"custom": 0,
		"istable": 1,
		"editable_grid": 1,
		"fields": [
			{"fieldname": "qc_type", "label": "Tipe QC", "fieldtype": "Select",
			 "options": "Kurva Kalibrasi\nRipitabilitas\nTrueness", "reqd": 1, "in_list_view": 1},
			{"fieldname": "nilai_slope", "label": "Nilai Slope", "fieldtype": "Float", "in_list_view": 1},
			{"fieldname": "nilai_intersep", "label": "Nilai Intersep", "fieldtype": "Float", "in_list_view": 1},
			{"fieldname": "nilai_r2", "label": "Nilai R2", "fieldtype": "Float", "in_list_view": 1},
			{"fieldname": "nilai_rpd_persen", "label": "Nilai RPD (%)", "fieldtype": "Percent"},
			{"fieldname": "nilai_trueness_persen", "label": "Nilai Trueness (%)", "fieldtype": "Percent"},
			{"fieldname": "keterangan", "label": "Keterangan", "fieldtype": "Small Text"},
		],
	})


def create_test_result():
	_create_if_missing({
		"doctype": "DocType",
		"name": "Test Result",
		"module": MODULE,
		"custom": 0,
		"track_changes": 1,
		"sort_field": "modified",
		"sort_order": "DESC",
		"fields": [
			{"fieldname": "sample", "label": "Sample", "fieldtype": "Link", "options": "Sample", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "work_order", "label": "Work Order", "fieldtype": "Link", "options": "Work Order Pengujian",
			 "reqd": 1, "fetch_from": "sample.work_order", "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "parameter", "label": "Parameter", "fieldtype": "Link", "options": "Test Parameter", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "analis", "label": "Analis", "fieldtype": "Link", "options": "Employee", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "hasil_uji", "label": "Hasil Uji", "fieldtype": "Float", "reqd": 1, "in_list_view": 1},
			{"fieldname": "satuan", "label": "Satuan", "fieldtype": "Data", "reqd": 1, "fetch_from": "parameter.satuan", "in_list_view": 1},
			{"fieldname": "qc_detail", "label": "Detail QC", "fieldtype": "Table", "options": "QC Detail"},
			{"fieldname": "status", "label": "Status", "fieldtype": "Select",
			 "options": "Draft\nDiajukan Validasi\nDivalidasi\nDitolak", "reqd": 1, "default": "Draft",
			 "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "validated_by", "label": "Divalidasi Oleh", "fieldtype": "Link", "options": "Employee"},
			{"fieldname": "validated_on", "label": "Divalidasi Pada", "fieldtype": "Datetime"},
			{"fieldname": "locked", "label": "Terkunci", "fieldtype": "Check", "default": "0"},
			{"fieldname": "catatan_validasi", "label": "Catatan Validasi", "fieldtype": "Small Text"},
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1, "email": 1, "share": 1},
		],
	})


def execute():
	create_qc_detail()
	create_test_result()
	frappe.db.commit()
	print("Test Result + QC Detail done.")
