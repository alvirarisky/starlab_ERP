frappe.ui.form.on("LHU", {
	refresh(frm) {
		// docstatus (bukan field status custom) jadi sumber kebenaran sekarang
		// bahwa LHU ini betul-betul Issued -- status tetap "Issued" (stale) di
		// LHU yang sudah di-cancel/amend, docstatus-nya yang berubah jadi 2.
		if (frm.is_new() || frm.doc.docstatus !== 1) return;

		frm.add_custom_button(__("Buat Invoice"), () => {
			frappe.call({
				method: "starlab_customizations.invoice_hooks.get_existing_invoice_for_lhu",
				args: { lhu: frm.doc.name },
				callback: (r) => {
					if (r.message) {
						frappe.set_route("Form", "Sales Invoice", r.message);
						return;
					}
					// Belum ada Invoice untuk LHU ini -- buka form baru (belum
					// disimpan) dengan Customer/Work Order/LHU sudah terisi.
					// Item & harga tetap harus dilengkapi manual oleh
					// Administrasi sebelum disimpan (lihat invoice_hooks.py).
					frappe.new_doc("Sales Invoice", {
						customer: frm.doc.customer,
						work_order: frm.doc.work_order,
						lhu: frm.doc.name,
					});
				},
			});
		});
	},
});
