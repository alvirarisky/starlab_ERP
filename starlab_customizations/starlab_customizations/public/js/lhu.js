frappe.ui.form.on("LHU", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.status !== "Issued") return;

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
