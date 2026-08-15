import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import flt, nowdate

from starlab_customizations.starlab_customizations.tests.quotation_test_utils import (
	TEST_ITEM_CODE,
	TEST_PARAMETER_NAME,
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


class IntegrationTestQuotationRushFeeInTotal(IntegrationTestCase):
	"""PRD v8 Sprint 12, TUGAS 1: rush_fee_amount (Sub Total x Rush Fee %)
	harus ikut mempengaruhi total_invoice. Rush Fee TIDAK ikut kena Discount
	(docs/keputusan_bisnis_terbaru.md #1, 2026-07-30) -- lihat catatan di
	quotation_hooks._calculate_price_summary."""

	def setUp(self):
		# harga_satuan di-fetch otomatis dari Test Parameter.harga_satuan_default
		# (lihat quotation_test_utils.ensure_master_data) -- tidak diisi manual
		# di sini karena fetch_from akan menimpanya saat insert/save.
		self.parameter_detail = [{"parameter": TEST_PARAMETER_NAME, "frekuensi": 1, "qty_per_titik": 1}]

	def test_rush_fee_amount_added_to_total_when_tier_set(self):
		normal = make_quotation(parameter_detail=self.parameter_detail)
		self.assertEqual(normal.rush_fee_amount, 0)

		doc = frappe.get_doc("Quotation", normal.name)
		doc.tingkat_percepatan = "5 Hari Kerja (+100%)"
		doc.save(ignore_permissions=True)
		reloaded = frappe.get_doc("Quotation", normal.name)

		self.assertEqual(reloaded.rush_fee_amount, reloaded.sub_total)
		self.assertGreater(reloaded.total_invoice, normal.total_invoice)

	def test_total_invoice_unchanged_when_normal(self):
		doc = make_quotation(parameter_detail=self.parameter_detail)
		self.assertEqual(doc.tingkat_percepatan, "Normal")
		self.assertEqual(doc.rush_fee_amount, 0)

		expected_total = doc.dpp + (doc.dpp * flt(doc.ppn_percent) / 100) + flt(doc.biaya_kirim)
		self.assertEqual(doc.total_invoice, expected_total)

	def test_discount_does_not_apply_to_rush_fee(self):
		doc = make_quotation(parameter_detail=self.parameter_detail)
		doc = frappe.get_doc("Quotation", doc.name)
		doc.tingkat_percepatan = "7 Hari Kerja (+80%)"
		doc.discount_percent = 10
		doc.save(ignore_permissions=True)
		reloaded = frappe.get_doc("Quotation", doc.name)

		discounted_sub_total = reloaded.sub_total - (
			reloaded.sub_total * flt(reloaded.discount_percent) / 100
		)
		expected_dpp = discounted_sub_total + reloaded.rush_fee_amount
		expected_total = (
			expected_dpp + (expected_dpp * flt(reloaded.ppn_percent) / 100) + flt(reloaded.biaya_kirim)
		)

		self.assertEqual(reloaded.dpp, expected_dpp)
		self.assertEqual(reloaded.total_invoice, expected_total)


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
