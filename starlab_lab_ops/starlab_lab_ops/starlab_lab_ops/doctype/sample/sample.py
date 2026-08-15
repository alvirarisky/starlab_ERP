# Copyright (c) 2026, Starlab and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Sample(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		catatan_kondisi: DF.SmallText | None
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
		retensi: DF.Literal["Tahan", "Bisa Dibuang"]
		sample_id: DF.Data
		status: DF.Literal["Diterima", "Sedang Diuji", "Divalidasi", "Diarsipkan", "Dimusnahkan"]
		tanggal_musnah: DF.Date | None
		tanggal_terima: DF.Date
		work_order: DF.Link
	# end: auto-generated types

	pass
