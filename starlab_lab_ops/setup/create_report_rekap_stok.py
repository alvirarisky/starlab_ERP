import os

import frappe

REPORT_NAME = "Rekap Stok Reagen dan Consumable"
MODULE = "Starlab Lab Ops"

QUERY = """
SELECT
	i.item_code as "Kode Item:Link/Item:120",
	i.item_name as "Nama Item::200",
	i.item_group as "Item Group::120",
	r.warehouse as "Warehouse:Link/Warehouse:150",
	IFNULL(b.actual_qty, 0) as "Stok Saat Ini:Float:110",
	r.warehouse_reorder_level as "Reorder Level:Float:110",
	i.stock_uom as "UOM::80"
FROM `tabItem` i
INNER JOIN `tabItem Reorder` r ON r.parent = i.name
LEFT JOIN `tabBin` b ON b.item_code = i.item_code AND b.warehouse = r.warehouse
WHERE
	(%(item_group)s = '' OR i.item_group = %(item_group)s)
	AND (%(warehouse)s = '' OR r.warehouse = %(warehouse)s)
ORDER BY i.item_code
"""

JS_CONTENT = '''frappe.query_reports["Rekap Stok Reagen dan Consumable"] = {
	"filters": [
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"default": "",
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"default": "",
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "stok_saat_ini" && data.reorder_level != null) {
			if (flt(data.stok_saat_ini) < flt(data.reorder_level)) {
				value = `<span style="color: white; background-color: #d1483e; padding: 2px 6px; border-radius: 3px;">${data.stok_saat_ini} (Kritis)</span>`;
			}
		}
		return value;
	},
};
'''


def execute():
	if not frappe.db.exists("Report", REPORT_NAME):
		frappe.get_doc({
			"doctype": "Report",
			"report_name": REPORT_NAME,
			"ref_doctype": "Item",
			"report_type": "Query Report",
			"module": MODULE,
			"is_standard": "Yes",
			"query": QUERY,
			"roles": [{"role": "System Manager"}],
		}).insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"Report '{REPORT_NAME}' created.")
	else:
		doc = frappe.get_doc("Report", REPORT_NAME)
		doc.query = QUERY
		doc.save(ignore_permissions=True)
		frappe.db.commit()
		print(f"Report '{REPORT_NAME}' already exists, query updated.")

	app_path = frappe.get_app_path("starlab_lab_ops")
	report_dir = os.path.join(app_path, "starlab_lab_ops", "report", frappe.scrub(REPORT_NAME))
	js_file = os.path.join(report_dir, frappe.scrub(REPORT_NAME) + ".js")
	os.makedirs(report_dir, exist_ok=True)
	with open(js_file, "w") as f:
		f.write(JS_CONTENT)
	print(f"Wrote report client script to {js_file}")
