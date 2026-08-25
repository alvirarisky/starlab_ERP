import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, nowdate

from starlab_lab_ops.starlab_lab_ops.tests.test_lhu_hooks import _ensure_customer, _ensure_employee

TEST_PARAM = "TEST-PARAMETER-WOE"


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


def _make_wo_with_sample(employee, customer, sample_id_prefix):
	# frappe.tests.IntegrationTestCase does not roll back between individual
	# test *methods* within the same class -- a literal sample_id reused by
	# setUp() across 2+ methods of the same class collides on the Sample
	# primary key on the second method. Suffix with a fresh hash per call.
	sample_id = f"{sample_id_prefix}-{frappe.generate_hash(length=8)}"
	wo = frappe.get_doc(
		{
			"doctype": "Work Order Pengujian",
			"customer": customer,
			"kegiatan": "Test WO Eksternal flow",
			"tanggal_wo": nowdate(),
			"penerimaan_sampel": employee,
			"wo_parameter_detail": [
				{
					"parameter": _ensure_test_parameter(),
					"sample_id_range": sample_id,
					"pj_analis": employee,
					"target_pengujian": add_days(nowdate(), 7),
					"status_pengujian": "Pending",
				}
			],
		}
	)
	wo.insert(ignore_permissions=True)

	sample = frappe.get_doc(
		{
			"doctype": "Sample",
			"sample_id": sample_id,
			"work_order": wo.name,
			"matriks": "Air Bersih",
			"tanggal_terima": nowdate(),
			"status": "Diterima",
			"retensi": "Tahan",
		}
	)
	sample.insert(ignore_permissions=True)
	return wo, sample


class IntegrationTestWOEksternalSubkonTrigger(IntegrationTestCase):
	"""Open question #1 (jawaban Starlab): begitu baris wo_parameter_detail
	ditandai Subkon, sistem otomatis bikin draft WO Eksternal -- bukan lagi
	murni penanda manual di luar sistem (lihat wo_hooks.handle_subkon_flagging)."""

	def setUp(self):
		employee = _ensure_employee()
		customer = _ensure_customer("Test Customer WOE Trigger")
		self.employee = employee
		self.wo, self.sample = _make_wo_with_sample(employee, customer, "WOE-TRIGGER-SAMPLE")

	def test_marking_subkon_creates_draft_wo_eksternal(self):
		doc = frappe.get_doc("Work Order Pengujian", self.wo.name)
		doc.wo_parameter_detail[0].status_pengujian = "Subkon"
		doc.save(ignore_permissions=True)

		reloaded = frappe.get_doc("Work Order Pengujian", self.wo.name)
		woe_name = reloaded.wo_parameter_detail[0].wo_eksternal
		self.assertTrue(woe_name)

		woe = frappe.get_doc("WO Eksternal", woe_name)
		self.assertEqual(woe.status, "Draft")
		self.assertEqual(woe.work_order, self.wo.name)
		self.assertEqual(woe.parameter_detail[0].parameter, TEST_PARAM)

	def test_unrelated_save_does_not_duplicate_wo_eksternal(self):
		doc = frappe.get_doc("Work Order Pengujian", self.wo.name)
		doc.wo_parameter_detail[0].status_pengujian = "Subkon"
		doc.save(ignore_permissions=True)

		doc = frappe.get_doc("Work Order Pengujian", self.wo.name)
		doc.catatan = "no-op edit"
		doc.save(ignore_permissions=True)

		self.assertEqual(frappe.db.count("WO Eksternal", {"work_order": self.wo.name}), 1)


class IntegrationTestWOEksternalApprovalAndBridge(IntegrationTestCase):
	"""Open question #1 (jawaban Starlab): approval WO Eksternal terjadi
	SEBELUM dikirim ke vendor (MT->MM->Direksi, mirip approval Quotation),
	dan hasil yang balik dari vendor harus ikut ke LHU lewat Test Result
	normal (status Diajukan Validasi, tetap lewat validasi Manajer Teknis)
	-- bukan lompat langsung ke Divalidasi. Lihat wo_eksternal_hooks.py."""

	def setUp(self):
		employee = _ensure_employee()
		customer = _ensure_customer("Test Customer WOE Approval")
		self.employee = employee
		self.wo, self.sample = _make_wo_with_sample(employee, customer, "WOE-APPROVAL-SAMPLE")

		doc = frappe.get_doc("Work Order Pengujian", self.wo.name)
		doc.wo_parameter_detail[0].status_pengujian = "Subkon"
		doc.save(ignore_permissions=True)
		reloaded = frappe.get_doc("Work Order Pengujian", self.wo.name)
		self.woe_name = reloaded.wo_parameter_detail[0].wo_eksternal

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_ajukan_blocked_while_fields_incomplete(self):
		woe = frappe.get_doc("WO Eksternal", self.woe_name)
		with self.assertRaises(frappe.ValidationError):
			apply_workflow(woe, "Ajukan")

		self.assertEqual(frappe.db.get_value("WO Eksternal", self.woe_name, "status"), "Draft")

	def test_full_approval_chain_creates_test_result_on_hasil_diterima(self):
		woe = frappe.get_doc("WO Eksternal", self.woe_name)
		woe.vendor_nama = "Lab Vendor Test"
		woe.tanggal_kirim = nowdate()
		woe.tanggal_target_kembali = add_days(nowdate(), 5)
		woe.pj_penerima_hasil = self.employee
		woe.parameter_detail[0].sample = self.sample.name
		woe.save(ignore_permissions=True)

		woe = frappe.get_doc("WO Eksternal", self.woe_name)
		apply_workflow(woe, "Ajukan")
		self.assertEqual(
			frappe.db.get_value("WO Eksternal", self.woe_name, "status"), "Menunggu Approval MT"
		)

		woe = frappe.get_doc("WO Eksternal", self.woe_name)
		apply_workflow(woe, "Setujui")
		self.assertEqual(
			frappe.db.get_value("WO Eksternal", self.woe_name, "status"), "Menunggu Approval MM"
		)

		woe = frappe.get_doc("WO Eksternal", self.woe_name)
		apply_workflow(woe, "Setujui")
		self.assertEqual(
			frappe.db.get_value("WO Eksternal", self.woe_name, "status"), "Menunggu Approval Direksi"
		)

		woe = frappe.get_doc("WO Eksternal", self.woe_name)
		apply_workflow(woe, "Setujui")
		self.assertEqual(frappe.db.get_value("WO Eksternal", self.woe_name, "status"), "Approved")

		woe = frappe.get_doc("WO Eksternal", self.woe_name)
		woe.parameter_detail[0].hasil_uji = 12.5
		woe.parameter_detail[0].status_hasil = "Diterima"
		woe.save(ignore_permissions=True)

		woe = frappe.get_doc("WO Eksternal", self.woe_name)
		test_result_name = woe.parameter_detail[0].test_result
		self.assertTrue(test_result_name)

		test_result = frappe.get_doc("Test Result", test_result_name)
		self.assertEqual(test_result.sample, self.sample.name)
		self.assertEqual(test_result.parameter, TEST_PARAM)
		self.assertEqual(test_result.analis, self.employee)
		self.assertEqual(float(test_result.hasil_uji), 12.5)
		self.assertEqual(test_result.status, "Diajukan Validasi")

		woe = frappe.get_doc("WO Eksternal", self.woe_name)
		woe.catatan = "no-op"
		woe.save(ignore_permissions=True)
		self.assertEqual(frappe.db.count("Test Result", {"sample": self.sample.name}), 1)
