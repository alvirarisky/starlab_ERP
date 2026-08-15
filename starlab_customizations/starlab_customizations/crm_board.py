import frappe
from frappe.model.workflow import WorkflowTransitionError, apply_workflow, get_workflow_name

# Kolom kanban Papan Quotation & Papan Client Inquiry = state Workflow yang
# SUDAH ADA di masing-masing doctype (fixtures/workflow.json), apa adanya --
# tidak ada status baru yang dikarang khusus buat board ini. Field yang
# nampung state itu BEDA namanya per doctype (Quotation pakai
# "workflow_state", Client Inquiry pakai "status" -- fixtures/workflow.json
# field workflow_state_field), jadi tidak pernah di-hardcode di bawah ini,
# selalu di-resolve lewat get_workflow_name()+Workflow.workflow_state_field.
BOARD_FIELDS = {
	"Client Inquiry": [
		"name",
		"nama_pt",
		"pic_nama",
		"matriks",
		"channel_asal",
		"estimasi_qty",
		"customer",
		"dicatat_oleh",
		"modified",
	],
	"Quotation": [
		"name",
		"party_name",
		"total_invoice",
		"tanggal_kadaluwarsa",
		"tingkat_percepatan",
		"client_inquiry",
		"workflow_state_since",
		"modified",
	],
}

# client_inquiry_hooks.py::sync_client_inquiry_from_kaji_ulang (TSD Bagian
# 6.1): transisi "Diajukan Kaji Ulang" -> "Disetujui MT"/"Ditolak MT" WAJIB
# lewat submit Kaji Ulang Tender (yang juga otomatis bikin Quotation Draft),
# bukan tombol Workflow langsung. fixtures/workflow.json sendiri secara
# teknis MENGIZINKAN Manajer Teknis men-trigger transisi ini langsung (role
# permission di level Workflow tidak tahu soal konvensi ini) -- kalau board
# meneruskan drag apa adanya ke apply_workflow, itu jadi jalan pintas yang
# melewati Kaji Ulang Tender & bikin Quotation Draft tidak pernah dibuat.
# Diblokir eksplisit di sini, terpisah dari (di atas) permission Workflow.
BOARD_BLOCKED_TRANSITIONS = {
	"Client Inquiry": {
		("Diajukan Kaji Ulang", "Disetujui MT"),
		("Diajukan Kaji Ulang", "Ditolak MT"),
	},
}


def _validate_board_doctype(doctype):
	if doctype not in BOARD_FIELDS:
		frappe.throw(frappe._("Papan untuk {0} tidak dikenal.").format(doctype))


def _get_state_field(doctype):
	workflow_name = get_workflow_name(doctype)
	if not workflow_name:
		frappe.throw(frappe._("{0} tidak punya Workflow aktif.").format(doctype))
	return workflow_name, frappe.get_cached_doc("Workflow", workflow_name).workflow_state_field


@frappe.whitelist()
def get_board_data(doctype):
	_validate_board_doctype(doctype)
	_workflow_name, state_field = _get_state_field(doctype)
	workflow = frappe.get_cached_doc("Workflow", _workflow_name)
	columns = [s.state for s in workflow.states]

	fields = list(dict.fromkeys([*BOARD_FIELDS[doctype], state_field]))
	# frappe.get_list (bukan get_all) -- permission-checked sama seperti list
	# view biasa, DocPerm role yang sudah ada (custom_docperm.json) yang
	# nentuin kartu siapa yang kelihatan, tidak ada logic permission baru.
	rows = frappe.get_list(doctype, fields=fields, limit_page_length=0, order_by="modified desc")

	board = {c: [] for c in columns}
	for row in rows:
		state = row.get(state_field)
		board.setdefault(state, []).append(row)

	return {"columns": columns, "board": board, "state_field": state_field}


@frappe.whitelist()
def get_board_transitions(doctype):
	_validate_board_doctype(doctype)
	workflow_name, _state_field = _get_state_field(doctype)
	workflow = frappe.get_cached_doc("Workflow", workflow_name)
	blocked = BOARD_BLOCKED_TRANSITIONS.get(doctype, set())

	return [
		{
			"state": t.state,
			"action": t.action,
			"next_state": t.next_state,
			"allowed": t.allowed,
			"blocked": (t.state, t.next_state) in blocked,
		}
		for t in workflow.transitions
	]


@frappe.whitelist()
def apply_board_transition(doctype: str, docname: str, action: str):
	_validate_board_doctype(doctype)
	doc = frappe.get_doc(doctype, docname)
	workflow_name, state_field = _get_state_field(doctype)
	from_state = doc.get(state_field)

	transition = frappe.get_all(
		"Workflow Transition",
		filters={"parent": workflow_name, "state": from_state, "action": action},
		fields=["next_state"],
		limit=1,
	)
	if transition and (from_state, transition[0].next_state) in BOARD_BLOCKED_TRANSITIONS.get(doctype, set()):
		frappe.throw(
			frappe._(
				"Transisi ini hanya bisa dilakukan lewat Kaji Ulang Tender terkait, bukan drag-and-drop di papan ini."
			),
			title=frappe._("Aksi Tidak Diizinkan"),
		)

	try:
		apply_workflow(doc, action)
	except WorkflowTransitionError:
		frappe.throw(
			frappe._("Kartu ini tidak bisa dipindah ke kolom tersebut dari status saat ini."),
			title=frappe._("Transisi Tidak Valid"),
		)

	doc.reload()
	return doc.as_dict()
