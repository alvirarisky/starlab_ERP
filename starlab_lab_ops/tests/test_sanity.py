import frappe
from frappe.tests import IntegrationTestCase


class TestSanity(IntegrationTestCase):
	def test_app_is_installed(self):
		self.assertIn("starlab_lab_ops", frappe.get_installed_apps())

	def test_required_apps_are_installed(self):
		self.assertIn("erpnext", frappe.get_installed_apps())
