# Copyright (c) 2026, Starlab and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TestResult(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from starlab_lab_ops.starlab_lab_ops.doctype.qc_detail.qc_detail import QCDetail

		analis: DF.Link
		catatan_validasi: DF.SmallText | None
		hasil_uji: DF.Float
		locked: DF.Check
		parameter: DF.Link
		qc_detail: DF.Table[QCDetail]
		sample: DF.Link
		satuan: DF.Data
		status: DF.Literal["Draft", "Diajukan Validasi", "Divalidasi", "Ditolak"]
		validated_by: DF.Link | None
		validated_on: DF.Datetime | None
		work_order: DF.Link
	# end: auto-generated types

	pass
