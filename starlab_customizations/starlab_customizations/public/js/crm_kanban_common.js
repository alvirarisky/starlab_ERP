frappe.provide("starlab_customizations.crm_board");

// Kelas dasar papan kanban, dipakai bareng oleh Papan Quotation & Papan
// Client Inquiry (quotation_board.js / client_inquiry_board.js). Kolom =
// state Workflow doctype terkait apa adanya (lihat crm_board.py) -- kelas
// ini TIDAK tahu apa-apa soal state spesifik, murni generik.
//
// Klik kartu -> navigasi ke Form Desk biasa (frappe.set_route), BUKAN panel
// custom di sebelah papan seperti referensi visual awal. Form Desk asli
// sudah otomatis bawa semua field custom + timeline comment/activity +
// section Connections tanpa kode tambahan sama sekali -- mencoba mount
// frappe.ui.form.Form kedua di dalam Dialog (opsi awal) ternyata jauh lebih
// berat dari perkiraan (bikin app-page shell bersarang penuh + listener
// beforeunload sendiri), jadi dipakai jalur aman yang sudah disetujui di
// plan sebagai fallback, bukan versi "panel" yang lebih rumit.
starlab_customizations.crm_board.Board = class CrmKanbanBoard {
	// amount_field: override di subclass (lihat quotation_board.js) kalau
	// board ini punya field nilai uang -- kalau di-set, header tiap kolom
	// nampilin total gabungan kartu di kolom itu (analog kartu "Perkiraan
	// Omzet" di referensi visual awal). null/undefined = tidak ditampilkan
	// (Client Inquiry belum ada nilai uang sampai jadi Quotation).
	amount_field = null;

	constructor({ wrapper, doctype, method_module = "starlab_customizations.crm_board" }) {
		this.wrapper = wrapper;
		this.doctype = doctype;
		this.method_module = method_module;
		this.transitions_by_state = {};
		this.make();
	}

	make() {
		this.$container = $('<div class="crm-kanban-board"></div>').appendTo(this.wrapper);
		this.reload();
	}

	reload() {
		this._set_loading(true);
		frappe.call({
			method: `${this.method_module}.get_board_transitions`,
			args: { doctype: this.doctype },
			callback: (r) => {
				this.transitions_by_state = this._index_transitions(r.message || []);
				frappe.call({
					method: `${this.method_module}.get_board_data`,
					args: { doctype: this.doctype },
					callback: (r2) => {
						this.columns = r2.message.columns;
						this.board = r2.message.board;
						this.state_field = r2.message.state_field;
						this.render();
						this._set_loading(false);
					},
					error: () => this._set_loading(false),
				});
			},
			error: () => this._set_loading(false),
		});
	}

	// Spinner kecil di dalam area papan sendiri (bukan frappe.dom.freeze() --
	// itu nge-overlay SELURUH layar termasuk sidebar/navbar, kerasa terlalu
	// berat cuma buat refresh data kartu).
	_set_loading(show) {
		this.$container.toggleClass("crm-kanban-board-loading", show);
		if (show && !this.$container.find(".crm-kanban-board-spinner").length) {
			this.$container.append('<div class="crm-kanban-board-spinner"><span></span></div>');
		} else if (!show) {
			this.$container.find(".crm-kanban-board-spinner").remove();
		}
	}

	_column_total_html(cards) {
		if (!this.amount_field || !cards.length) return "";
		const total = cards.reduce((sum, doc) => sum + (flt(doc[this.amount_field]) || 0), 0);
		if (!total) return "";
		return `<div class="crm-kanban-column-total">${frappe.format(total, {
			fieldtype: "Currency",
		})}</div>`;
	}

	_index_transitions(list) {
		const map = {};
		list.forEach((t) => {
			map[t.state] = map[t.state] || [];
			map[t.state].push(t);
		});
		return map;
	}

	render() {
		this.$container.empty();
		this.columns.forEach((state) => {
			const cards = this.board[state] || [];
			const total_html = this._column_total_html(cards);
			const $col = $(`
				<div class="crm-kanban-column" data-state="${frappe.utils.escape_html(state)}">
					<div class="crm-kanban-column-header">
						<div class="crm-kanban-column-title-row">
							<span class="crm-kanban-column-title">${frappe.utils.escape_html(__(state))}</span>
							<span class="crm-kanban-column-count">${cards.length}</span>
						</div>
						${total_html}
					</div>
					<div class="crm-kanban-column-body"></div>
				</div>
			`).appendTo(this.$container);
			const $body = $col.find(".crm-kanban-column-body");
			if (!cards.length) {
				$body.append(`<div class="crm-kanban-empty">${__("Kosong")}</div>`);
			}
			cards.forEach((doc) => this.render_card(doc, $body));
			this._wire_column_dnd($col);
		});
	}

	render_card(doc, $body) {
		const $card = $(this.card_html(doc)).appendTo($body);
		$card.attr("draggable", "true");
		$card.on("dragstart", (e) => {
			this._dragging_docname = doc.name;
			this._dragging_from_state = doc[this.state_field];
			e.originalEvent.dataTransfer.setData("text/plain", doc.name);
			setTimeout(() => $card.addClass("dragging"), 0);
		});
		$card.on("dragend", () => $card.removeClass("dragging"));
		$card.on("click", () => {
			if ($card.hasClass("dragging")) return;
			this.open_detail(doc.name);
		});
	}

	// Override di board turunan (lihat quotation_board.js / client_inquiry_board.js).
	card_html(doc) {
		return `<div class="crm-kanban-card" data-name="${frappe.utils.escape_html(
			doc.name
		)}">${frappe.utils.escape_html(doc.name)}</div>`;
	}

	open_detail(docname) {
		frappe.set_route("Form", this.doctype, docname);
	}

	_wire_column_dnd($col) {
		const target_state = $col.attr("data-state");
		$col.on("dragover", (e) => {
			e.preventDefault();
			const allowed = this._is_allowed(this._dragging_from_state, target_state);
			$col.toggleClass("drop-forbidden", !allowed);
			$col.toggleClass("drop-allowed", allowed);
		});
		$col.on("dragleave", () => $col.removeClass("drop-forbidden drop-allowed"));
		$col.on("drop", (e) => {
			e.preventDefault();
			$col.removeClass("drop-forbidden drop-allowed");
			const docname = this._dragging_docname;
			const from_state = this._dragging_from_state;
			if (!docname || from_state === target_state) return;

			const transition = this._find_transition(from_state, target_state);
			if (!transition) {
				frappe.show_alert({
					message: __(
						"Kartu ini tidak bisa dipindah ke kolom tersebut dari status saat ini."
					),
					indicator: "red",
				});
				return;
			}
			this._move_card(docname, from_state, target_state, transition.action);
		});
	}

	_find_transition(from_state, to_state) {
		if (!from_state) return null;
		const options = this.transitions_by_state[from_state] || [];
		return options.find((t) => t.next_state === to_state && !t.blocked) || null;
	}

	_is_allowed(from_state, to_state) {
		if (!from_state || from_state === to_state) return false;
		return !!this._find_transition(from_state, to_state);
	}

	_move_card(docname, from_state, to_state, action) {
		this.$container
			.find(`.crm-kanban-card[data-name="${frappe.utils.escape_html(docname)}"]`)
			.addClass("crm-kanban-card-loading");
		frappe.call({
			method: `${this.method_module}.apply_board_transition`,
			args: { doctype: this.doctype, docname, action },
			callback: (r) => {
				this._apply_local_move(docname, from_state, to_state, r.message);
				this.render();
				frappe.show_alert({
					message: __("Kartu dipindahkan ke {0}.", [__(to_state)]),
					indicator: "green",
				});
			},
			error: () => {
				frappe.show_alert({
					message: __("Gagal memindahkan kartu. Coba lagi."),
					indicator: "red",
				});
			},
		});
	}

	_apply_local_move(docname, from_state, to_state, updated_doc) {
		const list = this.board[from_state] || [];
		const idx = list.findIndex((d) => d.name === docname);
		let doc = idx > -1 ? list.splice(idx, 1)[0] : { name: docname };
		doc = Object.assign({}, doc, updated_doc, { [this.state_field]: to_state });
		this.board[to_state] = this.board[to_state] || [];
		this.board[to_state].unshift(doc);
	}
};
