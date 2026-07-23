frappe.query_reports["Status Sample Realtime"] = {
	"filters": [
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nDiterima\nSedang Diuji\nDivalidasi\nDiarsipkan\nDimusnahkan",
			"default": "",
		},
		{
			"fieldname": "matriks",
			"label": __("Matriks"),
			"fieldtype": "Select",
			"options": "\nUdara Ambien\nUdara Emisi\nAir Permukaan\nAir Bersih\nAir Limbah\nTanah\nSedimen\nKebisingan",
			"default": "",
		},
		{
			"fieldname": "work_order",
			"label": __("Work Order"),
			"fieldtype": "Link",
			"options": "Work Order Pengujian",
			"default": "",
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "status") {
			const colors = {
				"Diterima": "blue",
				"Sedang Diuji": "orange",
				"Divalidasi": "green",
				"Diarsipkan": "gray",
				"Dimusnahkan": "red",
			};
			const color = colors[data.status] || "gray";
			value = `<span class="indicator-pill ${color}">${data.status}</span>`;
		}
		return value;
	},
};
