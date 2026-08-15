import frappe
from frappe.utils import nowdate

TEST_ITEM_CODE = "TEST-ITEM-QUOTATION-PERM"
TEST_PARAMETER_NAME = "TEST-PARAMETER-QUOTATION-PERM"


def ensure_master_data():
	if not frappe.db.exists("UOM", "Nos"):
		frappe.get_doc({"doctype": "UOM", "uom_name": "Nos"}).insert(ignore_permissions=True)
	if not frappe.db.exists("Item Group", "All Item Groups"):
		frappe.get_doc({"doctype": "Item Group", "item_group_name": "All Item Groups", "is_group": 1}).insert(
			ignore_permissions=True
		)
	if not frappe.db.exists("Price List", "Standard Selling"):
		frappe.get_doc(
			{
				"doctype": "Price List",
				"price_list_name": "Standard Selling",
				"currency": "IDR",
				"selling": 1,
			}
		).insert(ignore_permissions=True)
	if not frappe.db.exists("Item", TEST_ITEM_CODE):
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": TEST_ITEM_CODE,
				"item_name": TEST_ITEM_CODE,
				"item_group": "All Item Groups",
				"stock_uom": "Nos",
				"is_stock_item": 0,
			}
		).insert(ignore_permissions=True)
	if not frappe.db.exists("Test Parameter", TEST_PARAMETER_NAME):
		frappe.get_doc(
			{
				"doctype": "Test Parameter",
				"parameter_name": TEST_PARAMETER_NAME,
				"matriks": "Air Bersih",
				"regulasi_acuan": "Test Regulation",
				"satuan": "mg/L",
				"status": "Aktif",
				# quotation_parameter_detail.harga_satuan pakai fetch_from
				# parameter.harga_satuan_default -- kalau kosong, harga_satuan
				# manapun yang di-set langsung di parameter_detail row bakal
				# ketiban 0 saat insert/save.
				"harga_satuan_default": 1000,
			}
		).insert(ignore_permissions=True)


def make_client_inquiry(customer=None):
	"""Client Inquiry minimal (status Draft) -- cukup buat referensi wajib
	Quotation.client_inquiry, tidak perlu melalui siklus Kaji Ulang Tender
	penuh untuk keperluan test permission/logika Quotation."""
	ensure_master_data()
	doc = frappe.get_doc(
		{
			"doctype": "Client Inquiry",
			"nama_pt": customer or "Test PT Client Inquiry",
			"customer": customer,
			"alamat": "Alamat Test",
			"pic_nama": "PIC Test",
			"matriks": "Air Bersih",
			"parameter_diminta": [{"parameter": TEST_PARAMETER_NAME}],
			"channel_asal": "WA",
			"dicatat_oleh": frappe.db.get_value("Employee", {}, "name"),
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def make_quotation(customer=None, client_inquiry=None, parameter_detail=None):
	ensure_master_data()
	customer = customer or frappe.db.get_value("Customer", {}, "name")
	client_inquiry = client_inquiry or make_client_inquiry(customer)
	doc = frappe.get_doc(
		{
			"doctype": "Quotation",
			"quotation_to": "Customer",
			"party_name": customer,
			"transaction_date": nowdate(),
			"selling_price_list": "Standard Selling",
			"currency": "IDR",
			"client_inquiry": client_inquiry,
			"items": [{"item_code": TEST_ITEM_CODE, "qty": 1, "rate": 100}],
			"parameter_detail": parameter_detail or [],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc
