# Copyright (c) 2026, Starlab and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class WOParameterDetail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		keterangan: DF.SmallText | None
		matriks: DF.Literal[
			"Udara Ambien",
			"Udara Emisi",
			"Air Permukaan",
			"Air Bersih",
			"Air Limbah",
			"Tanah",
			"Sedimen",
			"Kebisingan",
		]
		parameter: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		pj_analis: DF.Link
		sample_id_range: DF.Data
		status_pengujian: DF.Literal["Pending", "In Progress", "Done", "Subkon"]
		target_pengujian: DF.Date
	# end: auto-generated types

	pass
