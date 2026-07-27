import frappe
from frappe.model.workflow import WorkflowTransitionError, apply_workflow, get_transitions
from frappe.tests import IntegrationTestCase

from starlab_customizations.starlab_customizations.tests.quotation_test_utils import make_quotation

# Finance dan Marketing bukan approver Quotation (Finance: hanya perlu baca
# data untuk laporan keuangan; Marketing: hanya perlu baca untuk visibilitas
# pipeline penjualan -- lihat keputusan PO di ringkasan-seluruh-sprint.md).
# Alur approval final: MT -> MM -> Direksi. Test di bawah membuktikan kedua
# role tersebut tidak pernah punya workflow action apa pun di Quotation, di
# state manapun.
PENDING_APPROVAL_STATES = [
	"Menunggu Approval MT",
	"Menunggu Approval MM",
	"Menunggu Approval Direksi",
]

APPROVER_ROLES = {"Manajer Teknis", "Manajer Mutu", "Direksi", "Administrasi"}
NON_APPROVER_ROLES = {"Finance", "Marketing"}


class _QuotationNonApproverPermissionMixin:
	"""Mixin (BUKAN subclass TestCase) supaya tidak ikut ke-discover/dijalankan
	sebagai test class tersendiri -- cuma dipakai lewat multiple-inheritance
	di class konkret di bawah, yang masing-masing set `role` &
	`test_user_email`."""

	role = None
	test_user_email = None

	def setUp(self):
		self.test_user = self._ensure_role_only_user()
		self.quotation = make_quotation()

	def tearDown(self):
		frappe.set_user("Administrator")

	def _ensure_role_only_user(self):
		if not frappe.db.exists("User", self.test_user_email):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": self.test_user_email,
					"first_name": f"Test {self.role} QA",
					"send_welcome_email": 0,
				}
			)
			user.insert(ignore_permissions=True)
		else:
			user = frappe.get_doc("User", self.test_user_email)

		# User ini SENGAJA cuma boleh punya role target -- kalau ada role
		# approval lain (mis. dari test run sebelumnya) ikut nempel, test ini
		# jadi tidak murni menguji hak akses role target saja.
		other_roles = (APPROVER_ROLES | NON_APPROVER_ROLES) - {self.role}
		user.roles = [r for r in user.roles if r.role not in other_roles]
		if self.role not in {r.role for r in user.roles}:
			user.append("roles", {"role": self.role})
		user.save(ignore_permissions=True)
		return self.test_user_email

	def test_cannot_transition_at_any_pending_approval_state(self):
		for state in PENDING_APPROVAL_STATES:
			with self.subTest(state=state):
				frappe.set_user("Administrator")
				frappe.db.set_value("Quotation", self.quotation.name, "workflow_state", state)
				self.quotation.reload()

				frappe.set_user(self.test_user)

				transitions = get_transitions(self.quotation)
				self.assertEqual(
					transitions,
					[],
					f"{self.role} seharusnya tidak punya workflow transition apa pun di state '{state}'",
				)

				with self.assertRaises(WorkflowTransitionError):
					apply_workflow(self.quotation, "Setujui")

	def test_read_only_permission_on_quotation(self):
		meta_perms = frappe.permissions.get_role_permissions("Quotation", user=self.test_user)
		self.assertTrue(meta_perms.get("read"), f"{self.role} harus tetap bisa baca Quotation")
		self.assertFalse(meta_perms.get("write"), f"{self.role} tidak boleh punya hak edit Quotation")
		self.assertFalse(meta_perms.get("submit"), f"{self.role} tidak boleh punya hak submit Quotation")


class IntegrationTestQuotationFinancePermission(_QuotationNonApproverPermissionMixin, IntegrationTestCase):
	role = "Finance"
	test_user_email = "test.finance.quotation@example.com"


class IntegrationTestQuotationMarketingPermission(_QuotationNonApproverPermissionMixin, IntegrationTestCase):
	role = "Marketing"
	test_user_email = "test.marketing.quotation@example.com"
