frappe.query_reports["Rekap Kepatuhan Dokumen Mutu"] = {
	"filters": [
		{
			"fieldname": "document_level",
			"label": __("Level Dokumen"),
			"fieldtype": "Select",
			"options": "\nPM - Panduan Mutu\nPO - Prosedur Operasional\nIKM - Instruksi Kerja Metode\nDP - Dokumen Pendukung",
			"default": "",
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nDraft\nMenunggu Approval MM\nMenunggu Approval Direksi\nAktif\nDalam Revisi\nUsang",
			"default": "",
		},
		{
			"fieldname": "divisi",
			"label": __("Divisi"),
			"fieldtype": "Select",
			"options": "\nDireksi\nMM\nMT\nLaboratorium\nAdministrasi\nFinance\nMarketing",
			"default": "",
		},
	],
};
