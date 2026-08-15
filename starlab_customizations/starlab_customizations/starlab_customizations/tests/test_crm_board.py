import frappe
from frappe.tests import IntegrationTestCase

from starlab_customizations.crm_board import apply_board_transition, get_board_data, get_board_transitions
from starlab_customizations.starlab_customizations.tests.quotation_test_utils import (
	make_client_inquiry,
	make_quotation,
)


def _ensure_role_only_user(email, role, first_name):
	if not frappe.db.exists("User", email):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": first_name,
				"send_welcome_email": 0,
			}
		)
		user.insert(ignore_permissions=True)
	else:
		user = frappe.get_doc("User", email)
	if role not in {r.role for r in user.roles}:
		user.append("roles", {"role": role})
		user.save(ignore_permissions=True)
	return email


class IntegrationTestCrmBoard(IntegrationTestCase):
	"""Papan Quotation & Papan Client Inquiri (crm_board.py) -- lihat plan di
	docs; 2 hal yang WAJIB dikunci di sini:
	1. Nama field state beda antar doctype (Client Inquiry="status",
	   Quotation="workflow_state") -- tidak boleh pernah di-hardcode salah.
	2. Client Inquiry "Diajukan Kaji Ulang" -> Disetujui/Ditolak MT harus
	   diblokir dari papan (cuma boleh lewat Kaji Ulang Tender)."""

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_get_board_data_uses_correct_state_field_per_doctype(self):
		ci_name = make_client_inquiry()
		result = get_board_data("Client Inquiry")
		self.assertEqual(result["state_field"], "status")
		self.assertIn(ci_name, [d.name for d in result["board"].get("Draft", [])])

		quotation = make_quotation()
		result = get_board_data("Quotation")
		self.assertEqual(result["state_field"], "workflow_state")
		self.assertIn(quotation.name, [d.name for d in result["board"].get("Draft", [])])

	def test_apply_board_transition_moves_on_valid_action(self):
		quotation = make_quotation()
		apply_board_transition(doctype="Quotation", docname=quotation.name, action="Ajukan")
		self.assertEqual(
			frappe.db.get_value("Quotation", quotation.name, "workflow_state"), "Menunggu Approval MT"
		)

	def test_apply_board_transition_rejects_invalid_action_state_unchanged(self):
		quotation = make_quotation()
		with self.assertRaises(frappe.ValidationError):
			# "Setujui" tidak valid dari Draft (baru valid dari state Menunggu
			# Approval MT/MM/Direksi) -- harus ditolak, bukan diam-diam
			# mengubah state.
			apply_board_transition(doctype="Quotation", docname=quotation.name, action="Setujui")
		self.assertEqual(frappe.db.get_value("Quotation", quotation.name, "workflow_state"), "Draft")

	def test_non_approver_role_cannot_transition_quotation_via_board(self):
		quotation = make_quotation()
		frappe.db.set_value("Quotation", quotation.name, "workflow_state", "Menunggu Approval MT")

		user = _ensure_role_only_user(
			"test.marketing.crmboard@example.com", "Marketing", "Test Marketing CRM Board"
		)
		frappe.set_user(user)
		with self.assertRaises(frappe.ValidationError):
			apply_board_transition(doctype="Quotation", docname=quotation.name, action="Setujui")

		frappe.set_user("Administrator")
		self.assertEqual(
			frappe.db.get_value("Quotation", quotation.name, "workflow_state"), "Menunggu Approval MT"
		)

	def test_client_inquiry_transitions_flagged_blocked_in_get_board_transitions(self):
		transitions = get_board_transitions("Client Inquiry")
		blocked = [t for t in transitions if t["state"] == "Diajukan Kaji Ulang"]
		self.assertTrue(blocked, "Harus ada transisi keluar dari 'Diajukan Kaji Ulang'")
		self.assertTrue(
			all(t["blocked"] for t in blocked),
			"Semua transisi dari 'Diajukan Kaji Ulang' harus ditandai blocked",
		)

	def test_client_inquiry_diajukan_kaji_ulang_transition_blocked_via_board(self):
		# Manajer Teknis SECARA TEKNIS diizinkan oleh fixtures/workflow.json
		# men-trigger transisi ini langsung -- tapi TSD Bagian 6.1 mewajibkan
		# transisi ini cuma lewat submit Kaji Ulang Tender. Board harus
		# menolaknya duluan (BOARD_BLOCKED_TRANSITIONS), bukan cuma kebetulan
		# ketolong oleh permission role.
		ci_name = make_client_inquiry()
		frappe.db.set_value("Client Inquiry", ci_name, "status", "Diajukan Kaji Ulang")

		user = _ensure_role_only_user(
			"test.manajerteknis.crmboard@example.com", "Manajer Teknis", "Test Manajer Teknis CRM Board"
		)
		frappe.set_user(user)
		with self.assertRaises(frappe.ValidationError):
			apply_board_transition(doctype="Client Inquiry", docname=ci_name, action="Setujui")

		frappe.set_user("Administrator")
		self.assertEqual(frappe.db.get_value("Client Inquiry", ci_name, "status"), "Diajukan Kaji Ulang")
