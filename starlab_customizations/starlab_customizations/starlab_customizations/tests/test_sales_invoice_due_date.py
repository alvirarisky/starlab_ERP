import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, getdate, nowdate

from starlab_customizations.starlab_customizations.tests.quotation_test_utils import (
	TEST_ITEM_CODE,
	ensure_master_data,
)


class IntegrationTestSalesInvoiceDueDate(IntegrationTestCase):
	"""PRD v8 Sprint 12, item 7: due_date Sales Invoice = tanggal invoice + 7
	hari kalender (Term of Payment default SAI)."""

	def _make_invoice(self, posting_date=None):
		ensure_master_data()
		customer = frappe.db.get_value("Customer", {}, "name")
		company = frappe.defaults.get_global_default("company")
		income_account = frappe.db.get_value(
			"Account", {"company": company, "is_group": 0, "root_type": "Income"}, "name"
		)
		doc = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"customer": customer,
				"company": company,
				"posting_date": posting_date or nowdate(),
				# ERPNext memaksa posting_date balik ke hari ini kalau
				# set_posting_time tidak dicentang (proteksi anti-backdate
				# bawaan) -- perlu di-set eksplisit di sini supaya
				# posting_date custom di test ini beneran kepakai.
				"set_posting_time": 1,
				"items": [
					{
						"item_code": TEST_ITEM_CODE,
						"qty": 1,
						"rate": 100,
						"income_account": income_account,
					}
				],
			}
		)
		doc.insert(ignore_permissions=True)
		return doc

	def test_due_date_defaults_to_7_days_after_posting_date(self):
		doc = self._make_invoice(posting_date=nowdate())
		self.assertEqual(getdate(doc.due_date), getdate(add_days(nowdate(), 7)))

	def test_due_date_follows_custom_posting_date(self):
		posting_date = add_days(nowdate(), -20)
		doc = self._make_invoice(posting_date=posting_date)
		self.assertEqual(getdate(doc.due_date), getdate(add_days(posting_date, 7)))
