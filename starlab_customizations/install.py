import frappe

# TSD Bagian 9: "Aging Piutang" dan "Rekonsiliasi Bank" sudah tercakup oleh
# report native ERPNext (Accounts Receivable, Bank Reconciliation Statement)
# -- tidak perlu report custom. Satu-satunya yang kurang: keduanya default
# hanya untuk role "Accounts Manager"/"Accounts User"/"Auditor", sementara
# proyek ini pakai role custom "Finance".
#
# Report ini "is_standard": Yes -- menyimpan perubahan langsung ke field
# `roles`-nya ditolak Frappe di luar developer_mode ("Standard reports can
# only be created in developer mode"). Mekanisme resmi Frappe untuk
# menambah role akses ke standard report/page tanpa developer_mode adalah
# DocType "Custom Role" -- tapi custom_roles yang ada MENGGANTI (bukan
# menambah) daftar roles report aslinya (lihat get_custom_allowed_roles di
# frappe/core/doctype/report/report.py), jadi role asli harus disalin ulang
# supaya Accounts Manager/Accounts User/Auditor tidak kehilangan akses.
FINANCE_REPORT_ACCESS = ["Accounts Receivable", "Bank Reconciliation Statement"]


def after_migrate():
	for report_name in FINANCE_REPORT_ACCESS:
		if not frappe.db.exists("Report", report_name):
			continue

		existing_roles = frappe.get_all("Custom Role", filters={"report": report_name}, limit=1)
		if existing_roles:
			custom_role = frappe.get_doc("Custom Role", existing_roles[0].name)
			if any(r.role == "Finance" for r in custom_role.roles):
				continue
			custom_role.append("roles", {"role": "Finance"})
		else:
			report = frappe.get_doc("Report", report_name)
			custom_role = frappe.new_doc("Custom Role")
			custom_role.report = report_name
			custom_role.ref_doctype = report.ref_doctype
			for r in report.roles:
				custom_role.append("roles", {"role": r.role})
			custom_role.append("roles", {"role": "Finance"})

		custom_role.save(ignore_permissions=True)
