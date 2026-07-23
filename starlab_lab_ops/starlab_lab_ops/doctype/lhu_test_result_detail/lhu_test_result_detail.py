# Copyright (c) 2026, Starlab and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LHUTestResultDetail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		hasil_uji: DF.Float
		metode_acuan: DF.Data | None
		parameter: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		satuan: DF.Data | None
		test_result: DF.Link | None
	# end: auto-generated types

	pass
