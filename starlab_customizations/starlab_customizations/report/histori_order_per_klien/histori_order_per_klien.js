// Copyright (c) 2026, PT Starlab Analitik Indonesia and contributors
// For license information, please see license.txt

frappe.query_reports["Histori Order per Klien"] = {
	filters: [
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
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
