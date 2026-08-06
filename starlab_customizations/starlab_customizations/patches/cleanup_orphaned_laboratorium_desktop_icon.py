import frappe

# 2026-08-06: Workspace "Laboratorium" was deleted and merged into "LIMS"
# back on 2026-08-03 (see comment on ROLE_HOME_WORKSPACE in this app's
# install.py) -- but the *Workspace* record and its *Desktop Icon* / index
# ("modules" grid) counterpart are two independent things in Frappe (see
# _restrict_admin_workspaces_to_system_manager's comment on this same file
# for the full explanation of why). Deleting the Workspace file/record never
# touched the separately auto-created `Desktop Icon` (standard=0, so it's
# not owned by any app's fixtures either -- confirmed live) and
# `Workspace Sidebar` named "Laboratorium", so both kept showing up in the
# app/module icon grid indefinitely, pointing at nothing. Reported live by
# the user seeing a dead "Laboratorium" tile next to "LIMS" in that grid.
ORPHANED_NAME = "Laboratorium"


def execute():
	if frappe.db.exists("Workspace", ORPHANED_NAME):
		# Real Workspace exists again for some reason -- leave everything alone.
		return

	if frappe.db.exists("Desktop Icon", ORPHANED_NAME):
		frappe.delete_doc("Desktop Icon", ORPHANED_NAME, ignore_permissions=True, force=True)

	if frappe.db.exists("Workspace Sidebar", ORPHANED_NAME):
		frappe.delete_doc("Workspace Sidebar", ORPHANED_NAME, ignore_permissions=True, force=True)
