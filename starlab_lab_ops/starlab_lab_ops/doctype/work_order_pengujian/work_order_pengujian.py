# Copyright (c) 2026, Starlab and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class WorkOrderPengujian(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from starlab_lab_ops.starlab_lab_ops.doctype.wo_parameter_detail.wo_parameter_detail import WOParameterDetail

		catatan: DF.SmallText | None
		customer: DF.Link
		kegiatan: DF.Data
		naming_series: DF.Literal["P.SAI.####.MM.YYYY"]
		penerimaan_sampel: DF.Link
		quotation: DF.Link | None
		status: DF.Literal["Draft", "Approved", "In Progress", "Completed", "Cancelled"]
		tanggal_wo: DF.Date
		wo_parameter_detail: DF.Table[WOParameterDetail]
	# end: auto-generated types

	pass
