# Copyright (c) 2026, PT Starlab Analitik Indonesia and Contributors
# See license.txt

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests import IntegrationTestCase

from starlab_customizations.starlab_customizations.tests.quotation_test_utils import (
	TEST_PARAMETER_NAME,
	ensure_master_data,
)

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
# dicatat_oleh (Link -> Employee) -- auto-generating a fresh Employee test
# record recursively creates a Company, whose on_update default-Department
# seeding is broken in this sandbox ("Could not find Parent Department: All
# Departments"), unrelated to Client Inquiry itself (same root cause
# documented in starlab_quality's test_document_master.py). Tests below use
# an existing Employee (frappe.db.get_value), not an auto-generated one.
#
# customer (Link -> Customer) -- importing ERPNext's own test_customer.py
# (needed to check ITS ignore-list) runs erpnext.tests.utils.BootStrapTestData()
# as a MODULE-LEVEL side effect, which hits the exact same broken Department
# seeding above and blows up merely importing the module, before any test
# record generation even starts. Tests below always use an existing Customer
# (frappe.db.get_value), never need Frappe to auto-generate one.
IGNORE_TEST_RECORD_DEPENDENCIES = ["Employee", "Customer"]


def _make_client_inquiry_doc(**overrides):
	ensure_master_data()
	values = {
		"doctype": "Client Inquiry",
		"nama_pt": "Test PT Client Inquiry",
		"alamat": "Alamat Test",
		"pic_nama": "PIC Test",
		"matriks": "Air Bersih",
		"parameter_diminta": [{"parameter": TEST_PARAMETER_NAME}],
		"channel_asal": "WA",
		"dicatat_oleh": frappe.db.get_value("Employee", {}, "name"),
	}
	values.update(overrides)
	return frappe.get_doc(values)


class IntegrationTestClientInquiry(IntegrationTestCase):
	"""
	Integration tests for ClientInquiry.
	Use this class for testing interactions between multiple components.
	"""

	def test_default_status_is_draft(self):
		doc = _make_client_inquiry_doc()
		doc.insert(ignore_permissions=True)
		self.assertEqual(doc.status, "Draft")

	def test_ajukan_transition_moves_to_diajukan_kaji_ulang(self):
		doc = _make_client_inquiry_doc()
		doc.insert(ignore_permissions=True)

		apply_workflow(doc, "Ajukan")

		self.assertEqual(frappe.db.get_value("Client Inquiry", doc.name, "status"), "Diajukan Kaji Ulang")

	def test_alamat_is_mandatory(self):
		doc = _make_client_inquiry_doc(alamat=None)
		with self.assertRaises(frappe.MandatoryError):
			doc.insert(ignore_permissions=True)

	def test_parameter_diminta_requires_at_least_one_row(self):
		doc = _make_client_inquiry_doc(parameter_diminta=[])
		with self.assertRaises(frappe.MandatoryError):
			doc.insert(ignore_permissions=True)
