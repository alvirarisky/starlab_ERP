import frappe
from frappe.utils import flt


def on_update_petty_cash_entry(doc, method=None):
	before = doc.get_doc_before_save()
	if not before or before.status == doc.status:
		return

	# TSD Bagian 10 "Approval Pending": notifikasi segera begitu Petty Cash
	# Entry masuk ke state Menunggu Approval.
	if doc.status == "Menunggu Approval":
		from starlab_customizations.tasks import _notify_role

		_notify_role(
			"Direksi",
			frappe._("Petty Cash Entry {0} menunggu approval Anda").format(doc.name),
			frappe._("Petty Cash Entry {0} ({1}) menunggu approval Anda.").format(doc.name, doc.item),
		)

	if doc.status != "Disetujui":
		return

	_set_disetujui_oleh(doc)
	_create_journal_entry(doc)


def _set_disetujui_oleh(doc):
	if doc.disetujui_oleh:
		return
	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	if employee:
		doc.db_set("disetujui_oleh", employee, notify=True)


def _create_journal_entry(doc):
	# TODO(Finance SAI): nama akun di bawah ini masih placeholder -- belum ada
	# Chart of Accounts riil dari Finance yang dikonfirmasi. Sesuaikan
	# "Kas Kecil - {abbr}" / "Beban Operasional Kantor - {abbr}" begitu Finance
	# memastikan nama akun yang benar dipakai di COA produksi.
	company = frappe.defaults.get_global_default("company")
	if not company:
		_log_je_skip(doc, frappe._("tidak ada Company default yang terkonfigurasi di site ini"))
		return

	abbr = frappe.get_cached_value("Company", company, "abbr")
	credit_account = f"Kas Kecil - {abbr}"
	debit_account = f"Beban Operasional Kantor - {abbr}"

	if not frappe.db.exists("Account", credit_account) or not frappe.db.exists("Account", debit_account):
		_log_je_skip(
			doc,
			frappe._(
				"akun {0} / {1} belum ada di Chart of Accounts -- Finance perlu membuat akun "
				"tersebut (atau menyesuaikan nama akun di petty_cash_hooks.py) sebelum "
				"auto-generate Journal Entry bisa jalan"
			).format(credit_account, debit_account),
		)
		return

	# Expense (P&L) account -- ERPNext core requires a Cost Center on any GL
	# Entry against a Profit and Loss account.
	cost_center = frappe.get_cached_value("Company", company, "cost_center")
	if not cost_center:
		_log_je_skip(
			doc,
			frappe._(
				"Company {0} belum punya Cost Center default -- Finance perlu mengatur "
				"Cost Center default di Company sebelum auto-generate Journal Entry bisa jalan"
			).format(company),
		)
		return

	savepoint = "before_petty_cash_journal_entry"
	frappe.db.savepoint(savepoint)
	try:
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.company = company
		je.posting_date = doc.tanggal
		je.user_remark = frappe._("Petty Cash Entry {0}: {1}").format(doc.name, doc.item)
		je.append(
			"accounts",
			{"account": debit_account, "debit_in_account_currency": flt(doc.nominal), "cost_center": cost_center},
		)
		je.append("accounts", {"account": credit_account, "credit_in_account_currency": flt(doc.nominal)})
		je.insert(ignore_permissions=True)
		je.submit()
		doc.db_set("journal_entry", je.name, notify=True)
		doc.add_comment(
			"Info",
			frappe._("Journal Entry {0} dibuat otomatis oleh sistem karena Petty Cash Entry ini Disetujui.").format(
				je.name
			),
		)
	except Exception:
		frappe.db.rollback(save_point=savepoint)
		frappe.log_error(
			title="Auto-create Journal Entry dari Petty Cash Entry gagal",
			message=frappe.get_traceback(),
		)
		_log_je_skip(doc, frappe._("terjadi error saat membuat Journal Entry (lihat Error Log)"))


def _log_je_skip(doc, reason):
	doc.add_comment(
		"Info",
		frappe._(
			"Petty Cash Entry ini Disetujui, tapi Journal Entry gagal dibuat otomatis karena {0}. "
			"Finance perlu membuat Journal Entry secara manual dan mengisi field Journal Entry di sini."
		).format(reason),
	)
