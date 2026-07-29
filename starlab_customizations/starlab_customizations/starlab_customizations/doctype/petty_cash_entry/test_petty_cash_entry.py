# Copyright (c) 2026, PT Starlab Analitik Indonesia and Contributors
# See license.txt

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
# disetujui_oleh (Link -> Employee) -- auto-generating a fresh Employee test
# record recursively creates a Company, whose on_update default-Department
# seeding is broken in this sandbox ("Could not find Parent Department: All
# Departments"), unrelated to Petty Cash Entry itself (same root cause
# documented in starlab_quality's test_document_master.py). disetujui_oleh
# is only ever set automatically by petty_cash_hooks (via frappe.session.user
# lookup), never needs an auto-generated Employee record for these tests.
#
# journal_entry (Link -> Journal Entry) -- importing ERPNext's own
# test_journal_entry.py pulls in test_account.py, which (same as
# test_customer.py) imports erpnext.tests.utils and triggers
# BootStrapTestData() as a MODULE-LEVEL side effect, hitting the exact same
# broken Department seeding. journal_entry is only ever set automatically
# by petty_cash_hooks after a real Journal Entry is created in these tests
# themselves, never needs Frappe to auto-generate one.
IGNORE_TEST_RECORD_DEPENDENCIES = ["Employee", "Journal Entry"]


def _ensure_employee_linked_to_current_user():
	# petty_cash_hooks._set_disetujui_oleh looks up an Employee by
	# user_id == frappe.session.user -- link an existing Employee to the
	# test-running user so that lookup actually resolves (otherwise it
	# silently no-ops, which is correct production behavior for a
	# non-Employee system account, but not what these tests want to verify).
	employee = frappe.db.get_value("Employee", {}, "name")
	frappe.db.set_value("Employee", employee, "user_id", frappe.session.user)
	return employee


def _make_petty_cash_entry(nominal=100000):
	doc = frappe.get_doc(
		{
			"doctype": "Petty Cash Entry",
			"tanggal": nowdate(),
			"item": "ATK Kantor",
			"nominal": nominal,
			"bukti": "/files/test-bukti-petty-cash.png",
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


class IntegrationTestPettyCashEntry(IntegrationTestCase):
	"""
	Integration tests for PettyCashEntry.
	Use this class for testing interactions between multiple components.
	"""

	def test_nominal_must_be_positive(self):
		with self.assertRaises(frappe.ValidationError):
			_make_petty_cash_entry(nominal=0)

	def test_full_workflow_creates_journal_entry_on_disetujui(self):
		employee = _ensure_employee_linked_to_current_user()
		doc = _make_petty_cash_entry(nominal=150000)

		apply_workflow(doc, "Ajukan")
		doc.reload()
		apply_workflow(doc, "Setujui")
		doc.reload()

		self.assertEqual(doc.status, "Disetujui")
		self.assertEqual(doc.disetujui_oleh, employee)
		self.assertTrue(doc.journal_entry, "Journal Entry harus otomatis dibuat")

		je = frappe.get_doc("Journal Entry", doc.journal_entry)
		self.assertEqual(je.docstatus, 1)
		amounts = {row.account: (row.debit_in_account_currency, row.credit_in_account_currency) for row in je.accounts}
		company = frappe.defaults.get_global_default("company")
		abbr = frappe.get_cached_value("Company", company, "abbr")
		self.assertEqual(amounts.get(f"Beban Operasional Kantor - {abbr}"), (150000, 0))
		self.assertEqual(amounts.get(f"Kas Kecil - {abbr}"), (0, 150000))

	def test_locked_fields_after_disetujui(self):
		doc = _make_petty_cash_entry(nominal=50000)
		apply_workflow(doc, "Ajukan")
		doc.reload()
		apply_workflow(doc, "Setujui")
		doc.reload()

		doc.nominal = 999999
		with self.assertRaises(frappe.ValidationError):
			doc.save(ignore_permissions=True)

	def test_tolak_then_revisi_allows_edit_again(self):
		doc = _make_petty_cash_entry(nominal=75000)
		apply_workflow(doc, "Ajukan")
		doc.reload()
		apply_workflow(doc, "Tolak")
		doc.reload()
		self.assertEqual(doc.status, "Ditolak")

		apply_workflow(doc, "Revisi")
		doc.reload()
		self.assertEqual(doc.status, "Draft")

		doc.nominal = 80000
		doc.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Petty Cash Entry", doc.name, "nominal"), 80000)
