# Copyright (c) 2026, PT Starlab Analitik Indonesia and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PettyCashEntry(Document):
	def validate(self):
		if flt(self.nominal) <= 0:
			frappe.throw(frappe._("Nominal harus lebih besar dari 0"))

		before = self.get_doc_before_save()
		if before and before.status == "Disetujui":
			# Sudah di-posting ke Journal Entry -- field inti dikunci supaya
			# catatan akuntansi yang sudah jalan ke Accounting tidak berubah
			# diam-diam dari balik layar setelah faktanya.
			locked_fields = ("tanggal", "item", "nominal", "bukti", "keterangan")
			if any(self.get(f) != before.get(f) for f in locked_fields):
				frappe.throw(frappe._("Petty Cash Entry yang sudah Disetujui tidak bisa diubah lagi"))
