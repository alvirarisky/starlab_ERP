import frappe
from frappe.utils import nowdate

TEST_ITEM_CODE = "TEST-ITEM-QUOTATION-PERM"
TEST_PARAMETER_NAME = "TEST-PARAMETER-QUOTATION-PERM"
TEST_CUSTOMER_NAME = "Test Customer Quotation Perm"


def ensure_company():
	# CI/fresh-site: bench new-site never runs the Setup Wizard, so no
	# Company (and none of its dependent defaults) exists yet. Creating one
	# via ERPNext's own Company.on_update() (default warehouses/accounts)
	# additionally needs "Warehouse Type: Transit" to already exist -- it
	# doesn't ship without the wizard either. Both created here, once,
	# idempotently; on the long-lived dev site this whole function no-ops
	# since a Company already exists.
	company = frappe.db.get_value("Company", {}, "name")
	if not company:
		if not frappe.db.exists("Warehouse Type", "Transit"):
			frappe.get_doc({"doctype": "Warehouse Type", "name": "Transit"}).insert(ignore_permissions=True)

		company_doc = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Company CI",
				"abbr": "TCCI",
				"default_currency": "IDR",
				"country": "Indonesia",
			}
		)
		company_doc.insert(ignore_permissions=True)
		company = company_doc.name

	# Several hooks (petty_cash_hooks, client_inquiry_hooks, Sales Invoice
	# tests) read frappe.defaults.get_global_default("company")/"currency"
	# rather than querying Company directly -- a Company existing isn't
	# enough on its own, it also has to be THE default. Without this, new
	# documents fall back to Frappe's own hardcoded "INR" global currency
	# default regardless of the Company's actual default_currency, and then
	# fail "Party Account currency and document currency should be same".
	if not frappe.defaults.get_global_default("company"):
		frappe.defaults.set_global_default("company", company)
	currency = frappe.db.get_value("Company", company, "default_currency")
	if frappe.defaults.get_global_default("currency") != currency:
		frappe.defaults.set_global_default("currency", currency)

	# Setup Wizard also normally seeds the current Fiscal Year -- without
	# one, any dated transaction (Sales Invoice, Journal Entry, ...) fails
	# with "Date is not in any active Fiscal Year". Wide range so it stays
	# valid regardless of which year tests happen to run in.
	if not frappe.db.exists("Fiscal Year", {"year_start_date": ["<=", nowdate()], "year_end_date": [">=", nowdate()]}):
		frappe.get_doc(
			{
				"doctype": "Fiscal Year",
				"year": "CI 2020-2030",
				"year_start_date": "2020-01-01",
				"year_end_date": "2030-12-31",
			}
		).insert(ignore_permissions=True)

	return company


def ensure_employee():
	# Client Inquiry.dicatat_oleh (Link -> Employee, reqd=1) needs a real
	# Employee. Employee.insert() itself needs company + gender to exist.
	employee = frappe.db.get_value("Employee", {}, "name")
	if employee:
		return employee

	company = ensure_company()
	gender = frappe.db.get_value("Gender", {}, "name")
	if not gender:
		gender = "Other"
		frappe.get_doc({"doctype": "Gender", "gender": gender}).insert(ignore_permissions=True)

	employee_doc = frappe.get_doc(
		{
			"doctype": "Employee",
			"first_name": "Test Employee CI",
			"gender": gender,
			"date_of_birth": "1990-01-01",
			"date_of_joining": nowdate(),
			"status": "Active",
			"company": company,
		}
	)
	employee_doc.insert(ignore_permissions=True)
	return employee_doc.name


def ensure_customer():
	"""Any pre-existing Customer, or a freshly-created one -- several tests
	(Sales Invoice due date, Kaji Ulang Tender) just need *a* Customer to
	exist and don't care which one."""
	customer = frappe.db.get_value("Customer", {}, "name")
	if customer:
		return customer

	# is_group=0 (leaf) -- Customer.customer_group/territory reject a
	# group/folder node ("Cannot select a Group type Customer Group").
	customer_group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
	if not customer_group:
		customer_group = "Test Customer Group"
		frappe.get_doc(
			{"doctype": "Customer Group", "customer_group_name": customer_group, "is_group": 0}
		).insert(ignore_permissions=True)

	territory = frappe.db.get_value("Territory", {"is_group": 0}, "name")
	if not territory:
		territory = "Test Territory"
		frappe.get_doc({"doctype": "Territory", "territory_name": territory, "is_group": 0}).insert(
			ignore_permissions=True
		)

	frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": TEST_CUSTOMER_NAME,
			"customer_group": customer_group,
			"territory": territory,
		}
	).insert(ignore_permissions=True)
	return TEST_CUSTOMER_NAME


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
	ensure_company()


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
			"dicatat_oleh": ensure_employee(),
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def make_quotation(customer=None, client_inquiry=None, parameter_detail=None):
	ensure_master_data()
	customer = customer or ensure_customer()
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
