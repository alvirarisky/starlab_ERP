import frappe
from frappe.model.workflow import WorkflowTransitionError, apply_workflow, get_transitions
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate

# Finance bukan approver Quotation (lihat TUGAS 1 -- Finance hanya perlu baca
# data Quotation untuk keperluan laporan keuangan, bukan ikut alur approval
# MT -> MM -> Marketing -> Direksi). Test ini membuktikan role Finance tidak
# pernah punya workflow action apa pun di Quotation, di state manapun.
PENDING_APPROVAL_STATES = [
	"Menunggu Approval MT",
	"Menunggu Approval MM",
	"Menunggu Approval Marketing",
	"Menunggu Approval Direksi",
]

FINANCE_TEST_USER = "test.finance.quotation@example.com"
TEST_ITEM_CODE = "TEST-ITEM-QUOTATION-PERM"


class IntegrationTestQuotationFinancePermission(IntegrationTestCase):
	def setUp(self):
		self._ensure_master_data()
		self.finance_user = self._ensure_finance_only_user()
		self.quotation = self._make_quotation()

	def tearDown(self):
		frappe.set_user("Administrator")

	def _ensure_master_data(self):
		if not frappe.db.exists("UOM", "Nos"):
			frappe.get_doc({"doctype": "UOM", "uom_name": "Nos"}).insert(ignore_permissions=True)
		if not frappe.db.exists("Item Group", "All Item Groups"):
			frappe.get_doc(
				{"doctype": "Item Group", "item_group_name": "All Item Groups", "is_group": 1}
			).insert(ignore_permissions=True)
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

	def _ensure_finance_only_user(self):
		if not frappe.db.exists("User", FINANCE_TEST_USER):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": FINANCE_TEST_USER,
					"first_name": "Test Finance QA",
					"send_welcome_email": 0,
				}
			)
			user.insert(ignore_permissions=True)
		else:
			user = frappe.get_doc("User", FINANCE_TEST_USER)

		# User ini SENGAJA cuma boleh punya role Finance -- kalau ada role
		# approval lain (Manajer Teknis/Mutu/Marketing/Direksi) ikut nempel
		# (mis. dari test run sebelumnya), test ini jadi tidak murni menguji
		# hak akses Finance saja.
		approver_roles = {"Manajer Teknis", "Manajer Mutu", "Marketing", "Direksi", "Administrasi"}
		user.roles = [r for r in user.roles if r.role not in approver_roles]
		if "Finance" not in {r.role for r in user.roles}:
			user.append("roles", {"role": "Finance"})
		user.save(ignore_permissions=True)
		return FINANCE_TEST_USER

	def _make_quotation(self):
		customer = frappe.db.get_value("Customer", {}, "name")
		doc = frappe.get_doc(
			{
				"doctype": "Quotation",
				"quotation_to": "Customer",
				"party_name": customer,
				"transaction_date": nowdate(),
				"selling_price_list": "Standard Selling",
				"currency": "IDR",
				"items": [{"item_code": TEST_ITEM_CODE, "qty": 1, "rate": 100}],
			}
		)
		doc.insert(ignore_permissions=True)
		return doc

	def test_finance_cannot_transition_at_any_pending_approval_state(self):
		for state in PENDING_APPROVAL_STATES:
			with self.subTest(state=state):
				frappe.set_user("Administrator")
				frappe.db.set_value("Quotation", self.quotation.name, "workflow_state", state)
				self.quotation.reload()

				frappe.set_user(self.finance_user)

				transitions = get_transitions(self.quotation)
				self.assertEqual(
					transitions,
					[],
					f"Finance seharusnya tidak punya workflow transition apa pun di state '{state}'",
				)

				with self.assertRaises(WorkflowTransitionError):
					apply_workflow(self.quotation, "Setujui")

	def test_finance_read_only_permission_on_quotation(self):
		meta_perms = frappe.permissions.get_role_permissions("Quotation", user=self.finance_user)
		self.assertTrue(meta_perms.get("read"), "Finance harus tetap bisa baca Quotation (laporan keuangan)")
		self.assertFalse(meta_perms.get("write"), "Finance tidak boleh punya hak edit Quotation")
		self.assertFalse(meta_perms.get("submit"), "Finance tidak boleh punya hak submit Quotation")
