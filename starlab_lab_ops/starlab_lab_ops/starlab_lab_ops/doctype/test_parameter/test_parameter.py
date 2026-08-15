# Copyright (c) 2026, Starlab and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TestParameter(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		harga_satuan_default: DF.Currency
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
		metode_uji: DF.Link | None
		parameter_name: DF.Data
		regulasi_acuan: DF.Data
		satuan: DF.Data
		status: DF.Literal["Aktif", "Nonaktif"]
	# end: auto-generated types

	pass
