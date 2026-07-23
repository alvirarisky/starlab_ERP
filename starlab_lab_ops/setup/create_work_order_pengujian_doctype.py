import frappe

MODULE = "Starlab Lab Ops"
MATRIKS_OPTIONS = "Udara Ambien\nUdara Emisi\nAir Permukaan\nAir Bersih\nAir Limbah\nTanah\nSedimen\nKebisingan"


def _create_if_missing(doctype_dict):
	name = doctype_dict["name"]
	if frappe.db.exists("DocType", name):
		print(f"{name} already exists, skipping.")
		return
	frappe.get_doc(doctype_dict).insert()
	print(f"{name} created.")


def create_wo_parameter_detail():
	_create_if_missing({
		"doctype": "DocType",
		"name": "WO Parameter Detail",
		"module": MODULE,
		"custom": 0,
		"istable": 1,
		"editable_grid": 1,
		"fields": [
			{"fieldname": "matriks", "label": "Matriks", "fieldtype": "Select", "options": MATRIKS_OPTIONS, "in_list_view": 1},
			{"fieldname": "parameter", "label": "Parameter", "fieldtype": "Link", "options": "Test Parameter", "reqd": 1, "in_list_view": 1},
			{"fieldname": "sample_id_range", "label": "Range ID Sample", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
			{"fieldname": "pj_analis", "label": "PJ Analis", "fieldtype": "Link", "options": "Employee", "reqd": 1, "in_list_view": 1},
			{"fieldname": "target_pengujian", "label": "Target Pengujian", "fieldtype": "Date", "reqd": 1, "in_list_view": 1},
			{"fieldname": "status_pengujian", "label": "Status Pengujian", "fieldtype": "Select",
			 "options": "Pending\nIn Progress\nDone\nSubkon", "reqd": 1, "default": "Pending", "in_list_view": 1},
			{"fieldname": "keterangan", "label": "Keterangan", "fieldtype": "Small Text"},
		],
	})


def create_work_order_pengujian():
	_create_if_missing({
		"doctype": "DocType",
		"name": "Work Order Pengujian",
		"module": MODULE,
		"custom": 0,
		"autoname": "naming_series:",
		"naming_rule": "By \"Naming Series\" field",
		"track_changes": 1,
		"sort_field": "modified",
		"sort_order": "DESC",
		"fields": [
			{"fieldname": "naming_series", "label": "Naming Series", "fieldtype": "Select",
			 "options": "P.SAI.####.MM.YYYY", "reqd": 1},
			{"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "quotation", "label": "Quotation", "fieldtype": "Link", "options": "Quotation"},
			{"fieldname": "kegiatan", "label": "Kegiatan", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
			{"fieldname": "tanggal_wo", "label": "Tanggal WO", "fieldtype": "Date", "reqd": 1, "in_list_view": 1},
			{"fieldname": "status", "label": "Status", "fieldtype": "Select",
			 "options": "Draft\nApproved\nIn Progress\nCompleted\nCancelled", "reqd": 1, "default": "Draft",
			 "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "penerimaan_sampel", "label": "Penerimaan Sampel", "fieldtype": "Link", "options": "Employee", "reqd": 1},
			{"fieldname": "catatan", "label": "Catatan", "fieldtype": "Small Text"},
			{"fieldname": "wo_parameter_detail", "label": "Detail Parameter WO", "fieldtype": "Table", "options": "WO Parameter Detail", "reqd": 1},
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1, "email": 1, "share": 1},
		],
	})


def execute():
	create_wo_parameter_detail()
	create_work_order_pengujian()
	frappe.db.commit()
	print("Work Order Pengujian + WO Parameter Detail done.")
