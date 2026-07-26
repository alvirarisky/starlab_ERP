import io

import frappe
from frappe.utils.pdf import get_file_data_from_writer, get_pdf
from pypdf import PdfReader, PdfWriter


@frappe.whitelist()
def get_merged_quotation_pdf(quotation: str):
	# Gabungkan Cover/Company Profile + T&C + tabel harga dinamis + Lampiran A1
	# kosong jadi satu PDF (PRD v6 SS5.6), untuk tombol cetak satu-klik.
	#
	# Frappe tidak punya helper "merge_pdfs" siap pakai -- pola di bawah ini
	# meniru persis cara frappe.utils.print_format._download_multi_pdf
	# menggabungkan banyak dokumen: satu pypdf.PdfWriter yang di-append
	# berulang, baik dari file statis (PdfReader) maupun dari HTML yang
	# di-render (frappe.utils.pdf.get_pdf(..., output=writer)).
	doc = frappe.get_doc("Quotation", quotation)
	doc.check_permission("print")

	writer = PdfWriter()

	_append_attached_pdf(writer, frappe.db.get_single_value("Print Settings", "starlab_cover_quotation"))

	if doc.tnc_template:
		tnc = frappe.get_doc("TNC Master Template", doc.tnc_template)
		get_pdf(_tnc_html(tnc), {"margin-top": "15mm", "margin-bottom": "15mm"}, output=writer)

	frappe.get_print("Quotation", doc.name, "Quotation Ringkasan Harga", doc=doc, as_pdf=True, output=writer)

	_append_attached_pdf(writer, doc.lampiran_a1)

	frappe.local.response.filename = "{0}.pdf".format(doc.name.replace(" ", "-").replace("/", "-"))
	frappe.local.response.filecontent = get_file_data_from_writer(writer)
	frappe.local.response.type = "pdf"


def _append_attached_pdf(writer, file_url):
	# Cover/Company Profile & Lampiran A1 (kosong) adalah file PDF statis yang
	# di-attach (bukan doc/DocType yang bisa di-render Jinja), jadi di-append
	# apa adanya lewat pypdf, bukan lewat frappe.get_print.
	if not file_url:
		return
	file_doc = frappe.get_doc("File", {"file_url": file_url})
	writer.append_pages_from_reader(PdfReader(io.BytesIO(file_doc.get_content())))


def _tnc_html(tnc):
	return """
	<div style="font-family: Arial, sans-serif; font-size: 11px;">
	  <div style="text-align: center; font-weight: bold; font-size: 13px; text-decoration: underline; margin-bottom: 10px;">
	    SYARAT &amp; KETENTUAN
	  </div>
	  {0}
	</div>
	""".format(tnc.konten_tnc or "")
