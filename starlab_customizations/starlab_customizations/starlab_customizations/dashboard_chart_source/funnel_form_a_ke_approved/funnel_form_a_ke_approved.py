import frappe
from frappe import _
from frappe.utils.dashboard import cache_source


@frappe.whitelist()
@cache_source
def get(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
):
	# Workspace CRM: funnel konversi Form A (Client Inquiry) -> Quotation
	# dibuat -> Quotation Approved, lintas 2 DocType. Frappe versi ini TIDAK
	# punya tipe chart "Funnel" bawaan (opsi field `type` di Dashboard Chart
	# cuma Line/Bar/Percentage/Pie/Donut/Heatmap -- dicek langsung dari
	# dashboard_chart.json, bukan tebakan), jadi direpresentasikan sebagai
	# Bar chart menurun. Pola custom chart source ini sama persis dengan yang
	# dipakai ERPNext sendiri untuk chart lintas-DocType (lihat
	# erpnext/stock/dashboard_chart_source/warehouse_wise_stock_value/).
	client_inquiry_total = frappe.db.count("Client Inquiry")
	quotation_total = frappe.db.count("Quotation", {"docstatus": ["<", 2]})
	quotation_approved = frappe.db.count(
		"Quotation", {"docstatus": ["<", 2], "workflow_state": "Approved"}
	)

	return {
		"labels": [_("Form A (Client Inquiry)"), _("Quotation Dibuat"), _("Quotation Approved")],
		"datasets": [
			{
				"name": _("Jumlah"),
				"values": [client_inquiry_total, quotation_total, quotation_approved],
			}
		],
		"type": "bar",
	}
