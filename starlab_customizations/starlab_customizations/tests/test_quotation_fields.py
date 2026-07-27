import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate

from starlab_customizations.starlab_customizations.tests.quotation_test_utils import (
	TEST_ITEM_CODE,
	ensure_master_data,
	make_quotation,
)


class IntegrationTestQuotationClientInquiryMandatory(IntegrationTestCase):
	"""PRD v8 Sprint 12, item 3: client_inquiry wajib -- tidak ada lagi
	jalur bikin Quotation tanpa Form A."""

	def test_quotation_without_client_inquiry_is_rejected(self):
		ensure_master_data()
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
		with self.assertRaises(frappe.MandatoryError):
			doc.insert(ignore_permissions=True)

	def test_quotation_with_client_inquiry_succeeds(self):
		doc = make_quotation()
		self.assertTrue(doc.client_inquiry)


class IntegrationTestQuotationTingkatPercepatan(IntegrationTestCase):
	"""PRD v8 Sprint 12, item 4: tingkat_percepatan auto-fetch ke
	rush_fee_hari/rush_fee_percent untuk 2 tier terkonfirmasi."""

	def setUp(self):
		self.quotation = make_quotation()

	def _set_tier(self, tingkat_percepatan):
		doc = frappe.get_doc("Quotation", self.quotation.name)
		doc.tingkat_percepatan = tingkat_percepatan
		doc.save(ignore_permissions=True)
		return frappe.get_doc("Quotation", self.quotation.name)

	def test_5_hari_kerja_tier(self):
		doc = self._set_tier("5 Hari Kerja (+100%)")
		self.assertEqual(doc.rush_fee_hari, 5)
		self.assertEqual(doc.rush_fee_percent, 100)

	def test_7_hari_kerja_tier(self):
		doc = self._set_tier("7 Hari Kerja (+80%)")
		self.assertEqual(doc.rush_fee_hari, 7)
		self.assertEqual(doc.rush_fee_percent, 80)

	def test_normal_clears_rush_fee(self):
		self._set_tier("5 Hari Kerja (+100%)")
		doc = self._set_tier("Normal")
		self.assertEqual(doc.rush_fee_hari, 0)
		self.assertEqual(doc.rush_fee_percent, 0)

	def test_lainnya_keeps_manual_values(self):
		doc = frappe.get_doc("Quotation", self.quotation.name)
		doc.tingkat_percepatan = "Lainnya (Input Manual)"
		doc.rush_fee_hari = 3
		doc.rush_fee_percent = 50
		doc.save(ignore_permissions=True)

		reloaded = frappe.get_doc("Quotation", self.quotation.name)
		self.assertEqual(reloaded.rush_fee_hari, 3)
		self.assertEqual(reloaded.rush_fee_percent, 50)


class IntegrationTestTncMasterTemplateV2(IntegrationTestCase):
	"""PRD v8 Sprint 12, item 6: versi T&C baru (45 hari / pelunasan 7 hari),
	tanpa mengubah versi lama yang sudah dipakai Quotation lama."""

	def test_v02_content_has_updated_terms(self):
		tnc = frappe.get_doc("TNC Master Template", {"versi_template": "02"})
		self.assertIn("45 hari", tnc.konten_tnc)
		self.assertIn("7 (tujuh) hari kalender", tnc.konten_tnc)

	def test_v01_content_unchanged(self):
		tnc = frappe.get_doc("TNC Master Template", {"versi_template": "01"})
		self.assertIn("30 hari", tnc.konten_tnc)

	def test_new_quotation_uses_latest_version(self):
		doc = make_quotation()
		active = frappe.db.get_value("TNC Master Template", doc.tnc_template, "versi_template")
		self.assertEqual(active, "02")


class IntegrationTestCustomerKategoriPelanggan(IntegrationTestCase):
	"""PRD v8 Sprint 12, item 5: jenis_industri dan kategori_pelanggan
	dikonsolidasi jadi satu field."""

	def test_jenis_industri_field_no_longer_exists(self):
		self.assertIsNone(frappe.get_meta("Customer").get_field("jenis_industri"))

	def test_kategori_pelanggan_still_available_with_valid_options(self):
		field = frappe.get_meta("Customer").get_field("kategori_pelanggan")
		self.assertIsNotNone(field)
		self.assertIn("Perusahaan", field.options)
