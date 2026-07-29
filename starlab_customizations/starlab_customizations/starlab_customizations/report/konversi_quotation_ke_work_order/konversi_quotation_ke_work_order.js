// Copyright (c) 2026, PT Starlab Analitik Indonesia and contributors
// For license information, please see license.txt

frappe.query_reports["Konversi Quotation ke Work Order"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("Dari Tanggal"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("Sampai Tanggal"),
			fieldtype: "Date",
		},
	],
};
