// Copyright (c) 2026, PT Starlab Analitik Indonesia and contributors
// For license information, please see license.txt

// Tombol cetak satu-klik (PRD v6 SS5.6): menggabungkan Cover/Company Profile +
// T&C + tabel harga dinamis + Lampiran A1 kosong jadi satu PDF lewat
// starlab_customizations.quotation_print.get_merged_quotation_pdf, tanpa perlu
// export lalu buka aplikasi lain. Ini diinjeksikan lewat hooks.py doctype_js
// karena Quotation adalah DocType core ERPNext (tidak boleh mengedit
// quotation.js bawaan langsung).
frappe.ui.form.on("Quotation", {
	refresh(frm) {
		if (frm.doc.__islocal) {
			return;
		}
		frm.add_custom_button(__("Cetak Quotation (Gabungan)"), () => {
			const url = frappe.urllib.get_full_url(
				"/api/method/starlab_customizations.quotation_print.get_merged_quotation_pdf?quotation=" +
					encodeURIComponent(frm.doc.name)
			);
			window.open(url);
		});
	},
});
