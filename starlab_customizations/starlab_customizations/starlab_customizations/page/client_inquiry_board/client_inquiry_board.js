frappe.pages["client-inquiry-board"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Papan Client Inquiry"),
		single_column: true,
	});

	frappe.require("/assets/starlab_customizations/js/crm_kanban_common.js", () => {
		class ClientInquiryBoard extends starlab_customizations.crm_board.Board {
			card_html(doc) {
				const initials = (doc.dicatat_oleh || "").slice(0, 2).toUpperCase();
				// "Diajukan Kaji Ulang" -> "Disetujui MT"/"Ditolak MT" sengaja
				// diblokir dari drag (lihat crm_board.py::BOARD_BLOCKED_TRANSITIONS
				// -- server sudah menandai transisi ini "blocked": true, jadi board
				// generik otomatis menolaknya). Kartu di kolom ini dikasih tombol
				// pintas ke Kaji Ulang Tender, satu-satunya jalan resmi majuin
				// status ini (TSD Bagian 6.1).
				const show_kaji_ulang_button = doc.status === "Diajukan Kaji Ulang";

				return `
					<div class="crm-kanban-card" data-name="${frappe.utils.escape_html(doc.name)}">
						<div class="crm-kanban-card-title">${frappe.utils.escape_html(doc.nama_pt || doc.name)}</div>
						<div class="crm-kanban-card-subtitle">${frappe.utils.escape_html(doc.pic_nama || "")}</div>
						<div class="crm-kanban-card-badges">
							${
								doc.matriks
									? `<span class="crm-kanban-badge crm-kanban-badge-muted">${frappe.utils.escape_html(
											doc.matriks
									  )}</span>`
									: ""
							}
							${
								doc.channel_asal
									? `<span class="crm-kanban-badge crm-kanban-badge-muted">${frappe.utils.escape_html(
											doc.channel_asal
									  )}</span>`
									: ""
							}
							${
								doc.customer
									? `<span class="crm-kanban-badge crm-kanban-badge-success">${__(
											"Customer terdaftar"
									  )}</span>`
									: `<span class="crm-kanban-badge crm-kanban-badge-warning">${__(
											"Prospek baru"
									  )}</span>`
							}
						</div>
						<div class="crm-kanban-card-footer">
							${initials ? `<span class="crm-kanban-avatar">${frappe.utils.escape_html(initials)}</span>` : ""}
							${
								show_kaji_ulang_button
									? `<button class="btn btn-xs btn-default crm-kanban-kaji-ulang-btn">${__(
											"+ Buat Kaji Ulang Tender"
									  )}</button>`
									: ""
							}
						</div>
					</div>
				`;
			}

			render_card(doc, $body) {
				super.render_card(doc, $body);
				const $card = $body.find(`.crm-kanban-card[data-name="${doc.name}"]`);
				$card.find(".crm-kanban-kaji-ulang-btn").on("click", (e) => {
					e.stopPropagation();
					frappe.new_doc("Kaji Ulang Tender", { client_inquiry: doc.name });
				});
			}
		}

		wrapper.crm_board = new ClientInquiryBoard({
			wrapper: page.main,
			doctype: "Client Inquiry",
		});
	});
};

frappe.pages["client-inquiry-board"].refresh = function (wrapper) {
	if (wrapper.crm_board) {
		wrapper.crm_board.reload();
	}
};
