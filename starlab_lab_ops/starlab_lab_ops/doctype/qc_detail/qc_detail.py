# Copyright (c) 2026, Starlab and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class QCDetail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		keterangan: DF.SmallText | None
		nilai_intersep: DF.Float
		nilai_r2: DF.Float
		nilai_rpd_persen: DF.Percent
		nilai_slope: DF.Float
		nilai_trueness_persen: DF.Percent
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qc_type: DF.Literal["Kurva Kalibrasi", "Ripitabilitas", "Trueness"]
	# end: auto-generated types

	pass
