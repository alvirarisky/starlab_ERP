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
# revisi_history (child table Document Revision) has a Link field to
# Employee -- auto-generating a fresh Employee test record recursively
# creates a Company, whose on_update default-Department seeding is broken
# in this sandbox ("Could not find Parent Department: All Departments"),
# unrelated to anything Document Master itself does. None of the tests
# below rely on an auto-generated Employee record (the code path that
# would populate revisi_history, _append_revision_log in
# document_control_hooks.py, tolerates a missing Employee link fine), so
# skip walking that dependency chain entirely.
IGNORE_TEST_RECORD_DEPENDENCIES = ["Employee"]


def _make_document_master(document_no=None):
	doc = frappe.get_doc(
		{
			"doctype": "Document Master",
			"document_no": document_no or frappe.generate_hash(length=8),
			"document_name": "Dokumen Test Sanity",
			"document_level": "PO - Prosedur Operasional",
			"edisi_revisi": "01",
			"tanggal_efektif": nowdate(),
			"owner_division": "MM",
			"file_dokumen": "/files/test-document-master.pdf",
			"distribusi": [{"divisi": "MM", "tanggal_distribusi": nowdate()}],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


class IntegrationTestDocumentMaster(IntegrationTestCase):
	"""
	Integration tests for DocumentMaster.
	Use this class for testing interactions between multiple components.
	"""

	def test_workflow_draft_to_aktif(self):
		# TSD SS6.5 / starlab_quality/fixtures/workflow.json: siklus approval
		# Draft -> Menunggu Approval MM -> Menunggu Approval Direksi -> Aktif.
		doc = _make_document_master()
		self.assertEqual(doc.status, "Draft")

		apply_workflow(doc, "Ajukan")
		self.assertEqual(doc.status, "Menunggu Approval MM")

		apply_workflow(doc, "Setujui")
		self.assertEqual(doc.status, "Menunggu Approval Direksi")

		apply_workflow(doc, "Terbitkan")
		self.assertEqual(doc.status, "Aktif")

	def test_reject_at_mm_returns_to_draft_with_catatan_revisi(self):
		doc = _make_document_master()
		apply_workflow(doc, "Ajukan")

		doc.reload()
		doc.catatan_revisi = "Perlu perbaikan format"
		doc.save(ignore_permissions=True)

		apply_workflow(doc, "Tolak")
		self.assertEqual(doc.status, "Draft")

	def test_reject_at_mm_without_catatan_revisi_is_blocked(self):
		# document_control_hooks.validate_document_master: catatan_revisi
		# wajib diisi saat status turun dari tahap approval balik ke Draft.
		doc = _make_document_master()
		apply_workflow(doc, "Ajukan")

		doc.reload()
		doc.catatan_revisi = ""
		with self.assertRaises(frappe.ValidationError):
			apply_workflow(doc, "Tolak")

	def test_status_option_usang_exists_but_has_no_automatic_transition(self):
		# "Usang" tetap ada sebagai opsi Status (lihat description field di
		# document_master.json) untuk penandaan manual/historis -- tapi
		# TIDAK ADA transisi Workflow otomatis yang menujunya (keputusan PO
		# eksplisit: 1 record berputar lewat status-nya sendiri per edisi,
		# bukan 2 record terpisah lama/baru). Test ini mengunci perilaku itu:
		# menyelesaikan siklus penuh sampai Aktif TIDAK memicu status lain
		# manapun (termasuk Document Master lain) berubah jadi "Usang".
		status_field = frappe.get_meta("Document Master").get_field("status")
		self.assertIn("Usang", status_field.options)

		# Dihitung sebagai delta (sebelum/sesudah), bukan assert count == 0
		# -- ini shared dev DB, bukan DB kosong terisolasi per test. Record
		# "Usang" lama (mis. hasil penandaan manual lewat Desk) sah-sah saja
		# sudah ada dari sebelumnya; yang mau dikunci di sini murni "siklus
		# workflow ini tidak MENAMBAH satu pun Document Master baru berstatus
		# Usang", bukan "tabelnya harus kosong dari Usang sama sekali".
		usang_count_before = frappe.db.count("Document Master", {"status": "Usang"})

		doc = _make_document_master()
		apply_workflow(doc, "Ajukan")
		apply_workflow(doc, "Setujui")
		apply_workflow(doc, "Terbitkan")
		self.assertEqual(doc.status, "Aktif")
		self.assertEqual(
			frappe.db.count("Document Master", {"status": "Usang"}),
			usang_count_before,
			"Tidak ada jalur otomatis manapun di kode saat ini yang mengubah status jadi Usang",
		)
