from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, nowdate

from starlab_lab_ops.starlab_lab_ops.tests.test_lhu_hooks import _ensure_customer, _ensure_employee, _make_lhu

TEST_PARAM = "TEST-PARAMETER-WHATSAPP-NOTIFY"


def _ensure_test_parameter():
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
	return TEST_PARAM


class IntegrationTestSampleDiterimaWhatsApp(IntegrationTestCase):
	"""Open question #3 (jawaban Starlab): notifikasi WhatsApp ke customer +
	staff begitu sample diterima -- lihat wo_hooks.on_update_sample."""

	def setUp(self):
		self.employee = _ensure_employee()
		self.customer = _ensure_customer("Test Customer WhatsApp Sample")

		self.wo = frappe.get_doc(
			{
				"doctype": "Work Order Pengujian",
				"customer": self.customer,
				"kegiatan": "Test WhatsApp sample diterima",
				"tanggal_wo": nowdate(),
				"penerimaan_sampel": self.employee,
				"wo_parameter_detail": [
					{
						"parameter": _ensure_test_parameter(),
						"sample_id_range": f"WA-SAMPLE-{frappe.generate_hash(length=8)}",
						"pj_analis": self.employee,
						"target_pengujian": add_days(nowdate(), 7),
						"status_pengujian": "Pending",
					}
				],
			}
		)
		self.wo.insert(ignore_permissions=True)

	@patch("starlab_lab_ops.whatsapp_notify.notify_staff_and_customer")
	def test_sample_diterima_triggers_whatsapp_notify_once(self, mock_notify):
		sample_id = self.wo.wo_parameter_detail[0].sample_id_range
		sample = frappe.get_doc(
			{
				"doctype": "Sample",
				"sample_id": sample_id,
				"work_order": self.wo.name,
				"matriks": "Air Bersih",
				"tanggal_terima": nowdate(),
				"status": "Diterima",
				"retensi": "Tahan",
			}
		)
		sample.insert(ignore_permissions=True)

		mock_notify.assert_called_once()
		args, _ = mock_notify.call_args
		self.assertEqual(args[0], self.customer)

		# re-save without a status change must NOT notify again
		doc = frappe.get_doc("Sample", sample.name)
		doc.catatan_kondisi = "no-op"
		doc.save(ignore_permissions=True)
		mock_notify.assert_called_once()


class IntegrationTestLHUIssuedWhatsApp(IntegrationTestCase):
	"""Open question #3 (jawaban Starlab): notifikasi WhatsApp ke customer +
	staff begitu LHU terbit -- lihat lhu_hooks.on_submit."""

	@patch("starlab_lab_ops.whatsapp_notify.notify_staff_and_customer")
	def test_lhu_submit_triggers_whatsapp_notify(self, mock_notify):
		customer = _ensure_customer("Test Customer WhatsApp LHU")
		_make_lhu(customer)

		mock_notify.assert_called_once()
		args, _ = mock_notify.call_args
		self.assertEqual(args[0], customer)
