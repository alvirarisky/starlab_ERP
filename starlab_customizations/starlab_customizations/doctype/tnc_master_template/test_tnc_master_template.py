# Copyright (c) 2026, PT Starlab Analitik Indonesia and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
# diubah_oleh (Link -> Employee) -- auto-generating a fresh Employee test
# record recursively creates a Company, whose on_update default-Department
# seeding is broken in this sandbox ("Could not find Parent Department: All
# Departments"), unrelated to TNC Master Template itself (same root cause
# documented in starlab_quality's test_document_master.py). None of the
# tests below need an auto-generated Employee record.
IGNORE_TEST_RECORD_DEPENDENCIES = ["Employee"]


def _make_template(versi_template, berlaku_sejak=None, konten_tnc="Konten S&K test"):
	doc = frappe.get_doc(
		{
			"doctype": "TNC Master Template",
			"versi_template": versi_template,
			"berlaku_sejak": berlaku_sejak or nowdate(),
			"konten_tnc": konten_tnc,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


class IntegrationTestTNCMasterTemplate(IntegrationTestCase):
	"""
	Integration tests for TNCMasterTemplate.
	Use this class for testing interactions between multiple components.
	"""

	def test_versi_template_becomes_document_name(self):
		# autoname: field:versi_template
		doc = _make_template("TEST-VERSI-99")
		self.addCleanup(lambda: frappe.delete_doc("TNC Master Template", "TEST-VERSI-99", force=True))
		self.assertEqual(doc.name, "TEST-VERSI-99")

	def test_duplicate_versi_template_rejected(self):
		_make_template("TEST-VERSI-DUP")
		self.addCleanup(lambda: frappe.delete_doc("TNC Master Template", "TEST-VERSI-DUP", force=True))

		with self.assertRaises(frappe.DuplicateEntryError):
			_make_template("TEST-VERSI-DUP")

	def test_konten_tnc_is_mandatory(self):
		doc = frappe.get_doc(
			{
				"doctype": "TNC Master Template",
				"versi_template": "TEST-VERSI-NOKONTEN",
				"berlaku_sejak": nowdate(),
			}
		)
		with self.assertRaises(frappe.MandatoryError):
			doc.insert(ignore_permissions=True)
