frappe.query_reports["Rekap Stok Reagen dan Consumable"] = {
	filters: [
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options: "Item Group",
			default: "",
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
			default: "",
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "stok_saat_ini" && data.reorder_level != null) {
			if (flt(data.stok_saat_ini) < flt(data.reorder_level)) {
				value = `<span style="color: white; background-color: #d1483e; padding: 2px 6px; border-radius: 3px;">${data.stok_saat_ini} (Kritis)</span>`;
			}
		}
		return value;
	},
};
