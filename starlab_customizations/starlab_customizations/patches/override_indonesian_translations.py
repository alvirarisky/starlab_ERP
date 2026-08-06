import frappe

# 2026-08-06: _ensure_indonesian_language (install.py) turns on the stock
# id.po/id.mo catalog for frappe/erpnext core chrome -- a few of those
# built-in translations are wrong or inconsistent for how this project
# actually uses the terms (confirmed live, see docs/translation-activation.md):
#   - "Home" -> "Rumah" (literally "house/residence", not the standard
#     Indonesian term for app/site navigation "Home")
#   - "Quotation" -> "Penawaran" in the sidebar/breadcrumbs, while every
#     Number Card, hook, and doc comment elsewhere in this codebase calls it
#     "Quotation" -- overridden back to English for consistency with the
#     rest of the UI/code, not translated to "Penawaran" like the sidebar
#     alone would show.
#   - "Unpaid" -> "Tunggakan" (connotes overdue/in-arrears debt), which
#     collides in meaning with the separate "Overdue" -> "Terlambat"
#     translation -- an invoice can be Unpaid without being Overdue.
#   - "Sales Invoice" -> "Faktur penjualan" (wrong case; should be Title
#     Case to match how every other translated doctype label renders).
# frappe.get_doc({"doctype": "Translation", ...}) for an existing
# (source_text, language) pair takes precedence over the compiled .po
# catalog without needing to touch it -- this is the officially supported
# override mechanism (see docs/translation-activation.md).
OVERRIDES = [
	("Home", "Beranda"),
	("Quotation", "Quotation"),
	("Unpaid", "Belum Dibayar"),
	("Sales Invoice", "Faktur Penjualan"),
]


def execute():
	for source_text, translated_text in OVERRIDES:
		existing = frappe.db.exists("Translation", {"source_text": source_text, "language": "id"})
		if existing:
			frappe.db.set_value("Translation", existing, "translated_text", translated_text)
			continue
		frappe.get_doc(
			{
				"doctype": "Translation",
				"language": "id",
				"source_text": source_text,
				"translated_text": translated_text,
			}
		).insert(ignore_permissions=True)
