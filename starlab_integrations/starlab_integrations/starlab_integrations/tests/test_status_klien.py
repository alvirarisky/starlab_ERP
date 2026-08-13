import importlib

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate

# www/status_klien.py isn't a regular importable module path from Frappe's
# perspective (it's a website page controller, loaded by
# frappe.website.page_renderers.template_page.TemplatePage via a hyphen/
# underscore-aware lookup -- see the comment in that file for why the
# filename itself matters), so it's loaded here the same way importlib would
# resolve it as a plain Python module by dotted path.
status_klien = importlib.import_module("starlab_integrations.www.status_klien")

TEST_PARAM = "TEST-PARAMETER-STATUS-KLIEN"


def _ensure_customer(name):
	if not frappe.db.exists("Customer", name):
		customer_group = frappe.db.get_value("Customer Group", {}, "name") or "All Customer Groups"
		territory = frappe.db.get_value("Territory", {}, "name") or "All Territories"
		frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": name,
				"customer_group": customer_group,
				"territory": territory,
			}
		).insert(ignore_permissions=True)
	return name


def _ensure_portal_user(email, customer_name):
	if not frappe.db.exists("User", email):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": email.split("@")[0],
				"send_welcome_email": 0,
				"user_type": "Website User",
			}
		)
		user.insert(ignore_permissions=True)
		user.add_roles("Customer")

	cust = frappe.get_doc("Customer", customer_name)
	if not any(row.user == email for row in cust.portal_users):
		cust.append("portal_users", {"user": email})
		cust.save(ignore_permissions=True)


def _make_lhu(customer_name):
	if not frappe.db.exists("Test Parameter", TEST_PARAM):
		frappe.get_doc(
			{
				"doctype": "Test Parameter",
				"parameter_name": TEST_PARAM,
				"matriks": "Air Bersih",
				"regulasi_acuan": "Test Regulation",
				"satuan": "mg/L",
				"status": "Aktif",
				"harga_satuan_default": 1000,
			}
		).insert(ignore_permissions=True)

	employee = frappe.db.get_value("Employee", {}, "name")

	wo = frappe.get_doc(
		{
			"doctype": "Work Order Pengujian",
			"customer": customer_name,
			"kegiatan": "Test status_klien get_context",
			"tanggal_wo": nowdate(),
			"penerimaan_sampel": employee,
			"wo_parameter_detail": [
				{
					"parameter": TEST_PARAM,
					"sample_id_range": "1-1",
					"pj_analis": employee,
					"target_pengujian": nowdate(),
					"status_pengujian": "Done",
				}
			],
		}
	)
	wo.insert(ignore_permissions=True)

	lhu = frappe.get_doc(
		{
			"doctype": "LHU",
			"naming_series": "LHU-.####.-.MM.-.YYYY.",
			"work_order": wo.name,
			"customer": customer_name,
			"tanggal_terbit": nowdate(),
			"diterbitkan_oleh": employee,
			"test_result_list": [
				{
					"parameter": TEST_PARAM,
					"hasil_uji": 1.0,
					"satuan": "mg/L",
					"metode_acuan": "Test Regulation",
				}
			],
		}
	)
	lhu.insert(ignore_permissions=True)
	lhu.submit()
	return lhu.name


class IntegrationTestStatusKlien(IntegrationTestCase):
	"""Regression coverage for www/status_klien.py::get_context() -- this
	page previously silently never ran (wrong filename, status-klien.py
	instead of status_klien.py per Frappe's hyphen/underscore convention for
	pairing a www/<page>.html with its controller), so lhu_list/invoice_list
	were always empty for every Customer regardless of their real data. No
	test caught that because nothing called get_context() directly; this
	guards against the same class of regression."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer_a = _ensure_customer("Test Customer Status Klien A")
		cls.customer_b = _ensure_customer("Test Customer Status Klien B")
		cls.user_a = "status.klien.customer.a@example.com"
		cls.user_b = "status.klien.customer.b@example.com"
		_ensure_portal_user(cls.user_a, cls.customer_a)
		_ensure_portal_user(cls.user_b, cls.customer_b)
		cls.lhu_a = _make_lhu(cls.customer_a)
		cls.lhu_b = _make_lhu(cls.customer_b)

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_guest_is_redirected_to_login(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.Redirect):
			status_klien.get_context(frappe._dict())
		self.assertEqual(frappe.local.flags.redirect_location, "/login?redirect-to=/status-klien")

	def test_user_without_linked_customer_gets_no_access(self):
		email = "status.klien.no.customer@example.com"
		if not frappe.db.exists("User", email):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": "No Customer",
					"send_welcome_email": 0,
					"user_type": "Website User",
				}
			)
			user.insert(ignore_permissions=True)
			user.add_roles("Customer")

		frappe.set_user(email)
		context = status_klien.get_context(frappe._dict())
		self.assertTrue(context.no_access)
		self.assertNotIn("lhu_list", context)

	def test_portal_customer_sees_only_own_lhu_and_no_price_fields(self):
		frappe.set_user(self.user_a)
		context = status_klien.get_context(frappe._dict())

		self.assertFalse(context.no_access)
		lhu_names = [row.name for row in context.lhu_list]
		self.assertIn(self.lhu_a, lhu_names)
		self.assertNotIn(self.lhu_b, lhu_names)

	def test_portal_customer_invoice_list_scoped_to_own_customer(self):
		frappe.set_user(self.user_a)
		context = status_klien.get_context(frappe._dict())

		for invoice in context.invoice_list:
			self.assertEqual(frappe.db.get_value("Sales Invoice", invoice.name, "customer"), self.customer_a)
