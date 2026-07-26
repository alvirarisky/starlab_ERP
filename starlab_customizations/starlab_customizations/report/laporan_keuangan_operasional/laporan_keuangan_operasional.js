// Copyright (c) 2026, PT Starlab Analitik Indonesia and contributors
// For license information, please see license.txt

frappe.query_reports["Laporan Keuangan Operasional"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("Dari Tanggal"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("Sampai Tanggal"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "kategori",
			label: __("Kategori"),
			fieldtype: "Select",
			options: ["", "Petty Cash", "Entri Jurnal"],
		},
	],
};
