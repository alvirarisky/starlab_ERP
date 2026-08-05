import frappe


def log_system_field_change(doctype, name, changes, comment_text=None):
	# doc.db_set()/frappe.db.set_value() bypass Frappe's normal save() cycle
	# and, with it, Document.save_version() -- system-triggered auto-transitions
	# (not a user action through a Workflow Transition) never show up in the
	# Version/Track Changes log otherwise. This writes the Version entry Frappe
	# would have written itself for an equivalent normal save, so ISO 17025
	# audit trail requirements hold even for these system-triggered changes.
	# changes: dict of {fieldname: (old_value, new_value)}.
	version = frappe.new_doc("Version")
	version.ref_doctype = doctype
	version.docname = name
	version.data = frappe.as_json({"changed": [[field, old, new] for field, (old, new) in changes.items()]})
	version.insert(ignore_permissions=True)

	if comment_text:
		frappe.get_doc(
			{
				"doctype": "Comment",
				"comment_type": "Info",
				"reference_doctype": doctype,
				"reference_name": name,
				"content": comment_text,
			}
		).insert(ignore_permissions=True)
