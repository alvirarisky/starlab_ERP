frappe.pages["quotation-board"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Papan Quotation"),
		single_column: true,
	});

	frappe.require("/assets/starlab_customizations/js/crm_kanban_common.js", () => {
		class QuotationBoard extends starlab_customizations.crm_board.Board {
			amount_field = "total_invoice";

			card_html(doc) {
				const rush = doc.tingkat_percepatan && doc.tingkat_percepatan !== "Normal";
				const days_left = doc.tanggal_kadaluwarsa
					? frappe.datetime.get_diff(doc.tanggal_kadaluwarsa, frappe.datetime.now_date())
					: null;
				const expiry_soon = days_left !== null && days_left <= 7 && days_left >= 0;
				const expired = days_left !== null && days_left < 0;

				return `
					<div class="crm-kanban-card" data-name="${frappe.utils.escape_html(doc.name)}">
						<div class="crm-kanban-card-title">${frappe.utils.escape_html(doc.name)}</div>
						<div class="crm-kanban-card-subtitle">${frappe.utils.escape_html(doc.party_name || "")}</div>
						<div class="crm-kanban-card-amount">${frappe.format(doc.total_invoice || 0, {
							fieldtype: "Currency",
						})}</div>
						<div class="crm-kanban-card-badges">
							${
								rush
									? `<span class="crm-kanban-badge crm-kanban-badge-rush">${frappe.utils.escape_html(
											__(doc.tingkat_percepatan)
									  )}</span>`
									: ""
							}
							${
								doc.tanggal_kadaluwarsa
									? `<span class="crm-kanban-badge ${
											expired
												? "crm-kanban-badge-danger"
												: expiry_soon
												? "crm-kanban-badge-warning"
												: "crm-kanban-badge-muted"
									  }">
											${
												expired
													? __("Kedaluwarsa")
													: __("s/d {0}", [
															frappe.datetime.str_to_user(
																doc.tanggal_kadaluwarsa
															),
													  ])
											}
										</span>`
									: ""
							}
						</div>
						${
							doc.client_inquiry
								? `<div class="crm-kanban-card-footer">${__(
										"Form A"
								  )}: ${frappe.utils.escape_html(doc.client_inquiry)}</div>`
								: ""
						}
					</div>
				`;
			}
		}

		wrapper.crm_board = new QuotationBoard({ wrapper: page.main, doctype: "Quotation" });
	});
};

frappe.pages["quotation-board"].refresh = function (wrapper) {
	if (wrapper.crm_board) {
		wrapper.crm_board.reload();
	}
};
