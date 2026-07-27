import frappe
from frappe.desk.doctype.kanban_board.kanban_board import quick_kanban_board

# Kanban Board yang paling sering dicek harian oleh Laboratorium (Sample) &
# Manajer Teknis (Work Order Pengujian) -- dibuat lewat quick_kanban_board()
# bawaan Frappe (logika yang sama persis dengan tombol "Create Kanban Board"
# di List View), supaya kolomnya otomatis mengikuti opsi Select field
# "status" masing-masing DocType tanpa perlu di-hardcode manual di sini.
BOARDS = [
	("Sample", "Sample per Status"),
	("Work Order Pengujian", "Work Order Pengujian per Status"),
]


def execute():
	for doctype, board_name in BOARDS:
		if frappe.db.exists("Kanban Board", board_name):
			continue
		doc = quick_kanban_board(doctype, board_name, "status")
		doc.private = 0
		doc.save(ignore_permissions=True)
