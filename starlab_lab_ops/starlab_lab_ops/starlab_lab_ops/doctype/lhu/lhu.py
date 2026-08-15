# Copyright (c) 2026, Starlab and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LHU(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from starlab_lab_ops.starlab_lab_ops.doctype.lhu_test_result_detail.lhu_test_result_detail import (
			LHUTestResultDetail,
		)

		customer: DF.Link
		diterbitkan_oleh: DF.Link
		file_lhu: DF.Attach | None
		naming_series: DF.Literal["LHU-####-MM-YYYY"]
		status: DF.Literal["Draft", "Issued", "Revised", "Superseded"]
		tanggal_terbit: DF.Date
		test_result_list: DF.Table[LHUTestResultDetail]
		work_order: DF.Link
	# end: auto-generated types

	pass
