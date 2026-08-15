import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate

from starlab_lab_ops.lhu_hooks import get_permission_query_conditions, has_permission

TEST_PARAM = "TEST-PARAMETER-LHU-HOOKS"


def _ensure_customer(name):
	if not frappe.db.exists("Customer", name):
		# On a bare CI site (bench new-site without the Setup Wizard),
		# neither of the ERPNext defaults below exists yet -- falling back
		# to their literal names without creating them pointed customer_group
		# / territory at Customer Group / Territory records that don't
		# actually exist, so Customer.insert() failed link validation.
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
				"customer_name": name,
				"customer_group": customer_group,
				"territory": territory,
			}
		).insert(ignore_permissions=True)
	return name


def _ensure_employee():
	# Work Order Pengujian.penerimaan_sampel / wo_parameter_detail.pj_analis
	# (Link -> Employee) need a real Employee. Employee.insert() itself needs
	# a Company (+ "Warehouse Type: Transit" for Company.on_update's default
	# warehouses, + a Fiscal Year covering today for dated transactions, +
	# Gender) -- none of which exist on a bare CI site (bench new-site never
	# runs the Setup Wizard). Created here, once, idempotently; on the
	# long-lived dev site this whole chain no-ops since an Employee already
	# exists.
	employee = frappe.db.get_value("Employee", {}, "name")
	if employee:
		return employee

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
		frappe.defaults.set_global_default("company", company_doc.name)
		company = company_doc.name

	if not frappe.db.exists(
		"Fiscal Year", {"year_start_date": ["<=", nowdate()], "year_end_date": [">=", nowdate()]}
	):
		frappe.get_doc(
			{
				"doctype": "Fiscal Year",
				"year": "CI 2020-2030",
				"year_start_date": "2020-01-01",
				"year_end_date": "2030-12-31",
			}
		).insert(ignore_permissions=True)

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

	employee = _ensure_employee()

	wo = frappe.get_doc(
		{
			"doctype": "Work Order Pengujian",
			"customer": customer_name,
			"kegiatan": "Test lhu_hooks permission scoping",
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


class IntegrationTestLHUHooks(IntegrationTestCase):
	"""Regression coverage untuk row-level scoping Customer di lhu_hooks.py
	(audit finding C-5, docs/audit/LAPORAN_AUDIT.md) -- LHU punya Custom
	DocPerm "read" doctype-level untuk role Customer (dibutuhkan halaman
	Client Portal /status-klien), tapi tanpa filter row-level di sini,
	Customer manapun bisa baca LHU company LAIN lewat API langsung
	(/api/resource/LHU/<name>), bukan cuma lewat halaman portal yang sudah
	memfilter query-nya sendiri. Belum pernah ada test untuk ini sebelumnya
	meskipun ini fix Critical yang jadi dasar keamanan Client Portal."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer_a = _ensure_customer("Test Customer LHU Hooks A")
		cls.customer_b = _ensure_customer("Test Customer LHU Hooks B")
		cls.user_a = "lhu.hooks.customer.a@example.com"
		cls.user_b = "lhu.hooks.customer.b@example.com"
		_ensure_portal_user(cls.user_a, cls.customer_a)
		_ensure_portal_user(cls.user_b, cls.customer_b)
		cls.lhu_a = _make_lhu(cls.customer_a)
		cls.lhu_b = _make_lhu(cls.customer_b)

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_non_customer_user_has_no_row_restriction(self):
		self.assertEqual(get_permission_query_conditions("Administrator"), "")

	def test_customer_query_condition_scopes_to_own_customer_only(self):
		# get_parents_for_user() (erpnext) reads frappe.session.user directly,
		# ignoring the `user` arg below except for the role gate -- same as
		# real invocation, where Frappe always calls this hook for the
		# current session user anyway. Must set_user first or the erpnext
		# helper resolves against whatever session happens to be ambient.
		frappe.set_user(self.user_a)
		condition = get_permission_query_conditions(self.user_a)
		self.assertIn(self.customer_a, condition)
		self.assertNotIn(self.customer_b, condition)

	def test_customer_can_only_list_own_lhu(self):
		frappe.set_user(self.user_a)
		names = frappe.get_list("LHU", pluck="name")
		self.assertIn(self.lhu_a, names)
		self.assertNotIn(self.lhu_b, names)

	def test_has_permission_read_true_for_own_lhu(self):
		frappe.set_user(self.user_a)
		doc = frappe.get_doc("LHU", self.lhu_a)
		self.assertTrue(has_permission(doc, "read", self.user_a))

	def test_has_permission_read_false_for_other_customers_lhu(self):
		frappe.set_user(self.user_a)
		doc = frappe.get_doc("LHU", self.lhu_b)
		self.assertFalse(has_permission(doc, "read", self.user_a))

	def test_has_permission_write_always_false_for_customer(self):
		frappe.set_user(self.user_a)
		doc = frappe.get_doc("LHU", self.lhu_a)
		self.assertFalse(has_permission(doc, "write", self.user_a))
