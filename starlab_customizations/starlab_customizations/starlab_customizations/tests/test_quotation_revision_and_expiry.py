import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, nowdate

from starlab_customizations.starlab_customizations.tests.quotation_test_utils import make_quotation


class IntegrationTestQuotationRevisionReset(IntegrationTestCase):
	"""PRD v8 Sprint 12, item 1: konten yang diubah setelah sebagian
	disetujui (state Menunggu Approval MM / Direksi) wajib mereset seluruh
	approval -- balik ke Menunggu Approval MT, bukan "lanjut dari titik
	terakhir"."""

	def setUp(self):
		self.quotation = make_quotation()

	def test_content_change_at_mm_stage_resets_to_mt(self):
		frappe.db.set_value("Quotation", self.quotation.name, "workflow_state", "Menunggu Approval MM")
		doc = frappe.get_doc("Quotation", self.quotation.name)
		doc.discount_percent = 10
		doc.save(ignore_permissions=True)

		self.assertEqual(
			frappe.db.get_value("Quotation", self.quotation.name, "workflow_state"),
			"Menunggu Approval MT",
			"Perubahan konten di tahap MM harus mereset ke Menunggu Approval MT",
		)

	def test_content_change_at_direksi_stage_resets_to_mt(self):
		frappe.db.set_value("Quotation", self.quotation.name, "workflow_state", "Menunggu Approval Direksi")
		doc = frappe.get_doc("Quotation", self.quotation.name)
		doc.biaya_kirim = 50000
		doc.save(ignore_permissions=True)

		self.assertEqual(
			frappe.db.get_value("Quotation", self.quotation.name, "workflow_state"),
			"Menunggu Approval MT",
			"Perubahan konten di tahap Direksi tetap harus reset PENUH ke Menunggu Approval MT"
			" (bukan cuma mundur satu tahap ke MM)",
		)

	def test_no_content_change_does_not_reset_state(self):
		frappe.db.set_value("Quotation", self.quotation.name, "workflow_state", "Menunggu Approval MM")
		doc = frappe.get_doc("Quotation", self.quotation.name)
		doc.save(ignore_permissions=True)

		self.assertEqual(
			frappe.db.get_value("Quotation", self.quotation.name, "workflow_state"),
			"Menunggu Approval MM",
			"Save tanpa perubahan konten tidak boleh memicu reset",
		)

	def test_change_at_mt_stage_does_not_reset(self):
		# Belum ada approval sebelumnya untuk direset -- MT mengedit di
		# tahapnya sendiri sebelum approve pertama kali adalah hal normal.
		frappe.db.set_value("Quotation", self.quotation.name, "workflow_state", "Menunggu Approval MT")
		doc = frappe.get_doc("Quotation", self.quotation.name)
		doc.discount_percent = 5
		doc.save(ignore_permissions=True)

		self.assertEqual(
			frappe.db.get_value("Quotation", self.quotation.name, "workflow_state"),
			"Menunggu Approval MT",
		)


class IntegrationTestQuotationExpiry(IntegrationTestCase):
	"""PRD v8 Sprint 12, item 2: masa berlaku 45 hari, state Kedaluwarsa,
	dan reaktivasi tanpa perlu Quotation baru."""

	def setUp(self):
		self.quotation = make_quotation()

	def test_expiry_is_45_days_from_transaction_date(self):
		expected = add_days(self.quotation.transaction_date, 45)
		self.assertEqual(
			frappe.utils.getdate(self.quotation.tanggal_kadaluwarsa), frappe.utils.getdate(expected)
		)

	def test_scheduled_job_moves_approved_quotation_to_kedaluwarsa(self):
		frappe.db.set_value(
			"Quotation",
			self.quotation.name,
			{
				"workflow_state": "Approved",
				"docstatus": 1,
				"tanggal_kadaluwarsa": add_days(nowdate(), -1),
				"kedaluwarsa_notif_terkirim": 0,
			},
		)

		from starlab_customizations.tasks import check_quotation_expiry

		check_quotation_expiry()

		self.assertEqual(
			frappe.db.get_value("Quotation", self.quotation.name, "workflow_state"), "Kedaluwarsa"
		)

	def test_reactivation_extends_expiry_45_days_from_today(self):
		frappe.db.set_value(
			"Quotation",
			self.quotation.name,
			{
				"workflow_state": "Kedaluwarsa",
				"docstatus": 1,
				"tanggal_kadaluwarsa": add_days(nowdate(), -10),
			},
		)

		from frappe.model.workflow import apply_workflow

		doc = frappe.get_doc("Quotation", self.quotation.name)
		apply_workflow(doc, "Aktifkan Kembali")

		reloaded = frappe.get_doc("Quotation", self.quotation.name)
		self.assertEqual(reloaded.workflow_state, "Approved")
		self.assertEqual(
			frappe.utils.getdate(reloaded.tanggal_kadaluwarsa),
			frappe.utils.getdate(add_days(nowdate(), 45)),
		)

	def tearDown(self):
		frappe.set_user("Administrator")
