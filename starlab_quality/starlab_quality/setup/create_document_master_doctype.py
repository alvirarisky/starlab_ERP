import frappe

MODULE = "Starlab Quality"
DIVISI_OPTIONS = "Direksi\nMM\nMT\nLaboratorium\nAdministrasi\nFinance\nMarketing"


def _create_if_missing(doctype_dict):
	name = doctype_dict["name"]
	if frappe.db.exists("DocType", name):
		print(f"{name} already exists, skipping.")
		return
	frappe.get_doc(doctype_dict).insert()
	print(f"{name} created.")


def create_document_distribution():
	_create_if_missing({
		"doctype": "DocType",
		"name": "Document Distribution",
		"module": MODULE,
		"custom": 0,
		"istable": 1,
		"editable_grid": 1,
		"fields": [
			{"fieldname": "divisi", "label": "Divisi", "fieldtype": "Select", "options": DIVISI_OPTIONS, "reqd": 1, "in_list_view": 1},
			{"fieldname": "tanggal_distribusi", "label": "Tanggal Distribusi", "fieldtype": "Date", "reqd": 1, "in_list_view": 1},
			{"fieldname": "acknowledged", "label": "Acknowledged", "fieldtype": "Check", "in_list_view": 1},
			{"fieldname": "acknowledged_on", "label": "Acknowledged Pada", "fieldtype": "Datetime"},
		],
	})


def create_document_revision():
	_create_if_missing({
		"doctype": "DocType",
		"name": "Document Revision",
		"module": MODULE,
		"custom": 0,
		"istable": 1,
		"editable_grid": 1,
		"fields": [
			{"fieldname": "revisi_ke", "label": "Revisi Ke", "fieldtype": "Data", "in_list_view": 1},
			{"fieldname": "tanggal_revisi", "label": "Tanggal Revisi", "fieldtype": "Date", "in_list_view": 1},
			{"fieldname": "diubah_oleh", "label": "Diubah Oleh", "fieldtype": "Link", "options": "Employee", "in_list_view": 1},
			{"fieldname": "ringkasan_perubahan", "label": "Ringkasan Perubahan", "fieldtype": "Small Text"},
			{"fieldname": "file_versi_lama", "label": "File Versi Lama", "fieldtype": "Attach"},
		],
	})


def create_document_master():
	_create_if_missing({
		"doctype": "DocType",
		"name": "Document Master",
		"module": MODULE,
		"custom": 0,
		"autoname": "field:document_no",
		"naming_rule": "By fieldname",
		"track_changes": 1,
		"sort_field": "modified",
		"sort_order": "DESC",
		"fields": [
			{"fieldname": "document_no", "label": "Nomor Dokumen", "fieldtype": "Data", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "document_name", "label": "Nama Dokumen", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
			{"fieldname": "document_level", "label": "Level Dokumen", "fieldtype": "Select",
			 "options": "PM - Panduan Mutu\nPO - Prosedur Operasional\nIKM - Instruksi Kerja Metode\nDP - Dokumen Pendukung",
			 "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "edisi_revisi", "label": "Edisi/Revisi", "fieldtype": "Data", "reqd": 1},
			{"fieldname": "tanggal_efektif", "label": "Tanggal Efektif", "fieldtype": "Date", "reqd": 1},
			{"fieldname": "owner_division", "label": "Divisi Pemilik", "fieldtype": "Select",
			 "options": DIVISI_OPTIONS, "reqd": 1, "in_standard_filter": 1},
			{"fieldname": "status", "label": "Status", "fieldtype": "Select",
			 "options": "Aktif\nDalam Revisi\nUsang", "reqd": 1, "default": "Aktif",
			 "in_list_view": 1, "in_standard_filter": 1},
			{"fieldname": "file_dokumen", "label": "File Dokumen", "fieldtype": "Attach", "reqd": 1},
			{"fieldname": "distribusi", "label": "Distribusi", "fieldtype": "Table", "options": "Document Distribution", "reqd": 1},
			{"fieldname": "revisi_history", "label": "Riwayat Revisi", "fieldtype": "Table", "options": "Document Revision", "read_only": 1},
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1, "email": 1, "share": 1},
		],
	})


def execute():
	create_document_distribution()
	create_document_revision()
	create_document_master()
	frappe.db.commit()
	print("Document Master + child tables done.")
