# Copyright (c) 2026, PT Starlab Analitik Indonesia and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate

from starlab_customizations.starlab_customizations.tests.quotation_test_utils import (
	ensure_customer,
	make_client_inquiry,
)

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
# dinilai_oleh (Link -> Employee) -- auto-generating a fresh Employee test
# record recursively creates a Company, whose on_update default-Department
# seeding is broken in this sandbox ("Could not find Parent Department: All
# Departments"), unrelated to Kaji Ulang Tender itself (same root cause
# documented in starlab_quality's test_document_master.py). Tests below use
# an existing Employee (frappe.db.get_value), not an auto-generated one.
#
# customer (via Client Inquiry) -- importing ERPNext's own test_customer.py
# runs erpnext.tests.utils.BootStrapTestData() as a MODULE-LEVEL side effect,
# which hits the exact same broken Department seeding above and blows up
# merely importing the module. Tests below always use an existing Customer.
IGNORE_TEST_RECORD_DEPENDENCIES = ["Employee", "Customer"]


def _diajukan_kaji_ulang(customer=None):
	name = make_client_inquiry(customer=customer)
	frappe.db.set_value("Client Inquiry", name, "status", "Diajukan Kaji Ulang")
	return name


def _make_kaji_ulang_tender(client_inquiry, rekomendasi, catatan_kelayakan=None):
	doc = frappe.get_doc(
		{
			"doctype": "Kaji Ulang Tender",
			"client_inquiry": client_inquiry,
			"dinilai_oleh": frappe.db.get_value("Employee", {}, "name"),
			"tanggal_kaji": nowdate(),
			"rekomendasi": rekomendasi,
			"catatan_kelayakan": catatan_kelayakan,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def _comments_for(client_inquiry):
	return frappe.get_all(
		"Comment",
		filters={"reference_doctype": "Client Inquiry", "reference_name": client_inquiry},
		pluck="content",
	)


class IntegrationTestKajiUlangTender(IntegrationTestCase):
	"""
	Integration tests for KajiUlangTender.
	Use this class for testing interactions between multiple components.
	"""

	def setUp(self):
		# frappe.db.get_value("Customer", {}, "name") below assumes *some*
		# Customer already exists (true on the long-lived dev site) -- on a
		# bare CI site it's None otherwise, silently steering these tests
		# into the "no customer linked" code path instead of the one they
		# actually mean to exercise.
		ensure_customer()

	def test_layak_approves_client_inquiry(self):
		customer = frappe.db.get_value("Customer", {}, "name")
		client_inquiry = _diajukan_kaji_ulang(customer=customer)

		_make_kaji_ulang_tender(client_inquiry, "Layak")

		self.assertEqual(frappe.db.get_value("Client Inquiry", client_inquiry, "status"), "Disetujui MT")

	def test_layak_dengan_catatan_also_approves(self):
		customer = frappe.db.get_value("Customer", {}, "name")
		client_inquiry = _diajukan_kaji_ulang(customer=customer)

		_make_kaji_ulang_tender(client_inquiry, "Layak dengan Catatan", catatan_kelayakan="Catatan tambahan")

		self.assertEqual(frappe.db.get_value("Client Inquiry", client_inquiry, "status"), "Disetujui MT")

	def test_quotation_draft_auto_create_currently_fails_gracefully(self):
		# TSD/PRD Bagian 5 (placeholder table): Test Parameter belum
		# ditautkan ke Item master ERPNext, jadi _create_quotation_draft
		# SENGAJA tidak mengisi tabel `items` standar Quotation -- yang
		# berarti ERPNext core (accounts_controller totals calc) SELALU
		# gagal insert Quotation ini apa pun data test-nya, sampai keputusan
		# PO soal mapping Item turun (1 Item generik vs mapping per
		# parameter). Approval Client Inquiry-nya sendiri tetap harus sukses
		# -- Quotation Draft murni convenience di atasnya, bukan prasyarat
		# (lihat catatan di client_inquiry_hooks._create_quotation_draft).
		# Test ini MENGUNCI perilaku degradasi anggun itu supaya kegagalan
		# auto-create tidak diam-diam berubah jadi exception yang membatalkan
		# approval -- kalau nanti keputusan Item master turun dan ini mulai
		# berhasil bikin Quotation, sesuaikan assertion di sini.
		customer = frappe.db.get_value("Customer", {}, "name")
		client_inquiry = _diajukan_kaji_ulang(customer=customer)

		_make_kaji_ulang_tender(client_inquiry, "Layak")

		self.assertEqual(frappe.db.get_value("Client Inquiry", client_inquiry, "status"), "Disetujui MT")
		quotation = frappe.db.get_value("Quotation", {"client_inquiry": client_inquiry}, "name")
		self.assertFalse(quotation)
		comments = _comments_for(client_inquiry)
		self.assertTrue(
			any("gagal dibuat otomatis" in c for c in comments),
			"Harus ada catatan bahwa Quotation Draft gagal dibuat otomatis, bukan silent failure",
		)

	def test_tidak_layak_rejects_without_creating_quotation(self):
		customer = frappe.db.get_value("Customer", {}, "name")
		client_inquiry = _diajukan_kaji_ulang(customer=customer)

		_make_kaji_ulang_tender(client_inquiry, "Tidak Layak")

		self.assertEqual(frappe.db.get_value("Client Inquiry", client_inquiry, "status"), "Ditolak MT")
		quotation = frappe.db.get_value("Quotation", {"client_inquiry": client_inquiry}, "name")
		self.assertFalse(quotation, "Tidak boleh ada Quotation dibuat saat rekomendasi Tidak Layak")

	def test_no_customer_linked_adds_manual_creation_note(self):
		# client_inquiry_hooks._create_quotation_draft: tanpa Customer
		# terdaftar, auto-create degradasi ke catatan manual (beda pesan
		# dari kasus item-mapping di atas), bukan error.
		client_inquiry = _diajukan_kaji_ulang(customer=None)

		_make_kaji_ulang_tender(client_inquiry, "Layak")

		self.assertEqual(frappe.db.get_value("Client Inquiry", client_inquiry, "status"), "Disetujui MT")
		quotation = frappe.db.get_value("Quotation", {"client_inquiry": client_inquiry}, "name")
		self.assertFalse(quotation)
		comments = _comments_for(client_inquiry)
		self.assertTrue(
			any("belum tertaut ke Customer terdaftar" in c for c in comments),
			"Harus ada catatan spesifik soal Customer belum tertaut",
		)

	def test_resave_after_resolved_does_not_retrigger(self):
		# Edit catatan_kelayakan pasca-resolusi (mis. typo fix) tidak boleh
		# memicu ulang transisi/percobaan auto-create kedua kalinya.
		customer = frappe.db.get_value("Customer", {}, "name")
		client_inquiry = _diajukan_kaji_ulang(customer=customer)

		kaji = _make_kaji_ulang_tender(client_inquiry, "Layak")
		comment_count_after_first_save = len(_comments_for(client_inquiry))

		kaji.catatan_kelayakan = "Revisi catatan"
		kaji.save(ignore_permissions=True)

		self.assertEqual(len(_comments_for(client_inquiry)), comment_count_after_first_save)
