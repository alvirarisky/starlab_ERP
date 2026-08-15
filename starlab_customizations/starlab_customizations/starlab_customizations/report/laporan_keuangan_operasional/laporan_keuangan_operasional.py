import frappe
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "Tanggal", "fieldname": "tanggal", "fieldtype": "Date", "width": 100},
		{"label": "Kategori", "fieldname": "kategori", "fieldtype": "Data", "width": 120},
		{"label": "Referensi", "fieldname": "referensi", "fieldtype": "Data", "width": 150},
		{"label": "Keterangan", "fieldname": "keterangan", "fieldtype": "Data", "width": 250},
		{"label": "Nominal", "fieldname": "nominal", "fieldtype": "Currency", "width": 130},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
		{"label": "Saldo Kas Kecil", "fieldname": "saldo", "fieldtype": "Currency", "width": 140},
	]


def get_data(filters):
	rows = []
	kategori = filters.get("kategori")

	if not kategori or kategori == "Petty Cash":
		conditions = []
		values = {}
		if filters.get("from_date"):
			conditions.append("tanggal >= %(from_date)s")
			values["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			conditions.append("tanggal <= %(to_date)s")
			values["to_date"] = filters["to_date"]
		where_clause = " AND " + " AND ".join(conditions) if conditions else ""
		petty_cash = frappe.db.sql(
			f"""
			SELECT name, tanggal, item, nominal, status
			FROM `tabPetty Cash Entry`
			WHERE 1=1 {where_clause}
			ORDER BY tanggal DESC
			LIMIT 5000
			""",
			values,
			as_dict=1,
		)
		for pc in petty_cash:
			rows.append(
				{
					"tanggal": pc.tanggal,
					"kategori": "Petty Cash",
					"referensi": pc.name,
					"keterangan": pc.item,
					"nominal": pc.nominal,
					"status": pc.status,
					# Petty Cash Entry adalah catatan pengajuan/approval, bukan
					# mutasi buku besar itu sendiri -- saldo hanya dihitung dari
					# Journal Entry yang benar-benar membukukan ke akun Kas
					# Kecil (lihat _attach_saldo_kas_kecil).
					"saldo": None,
				}
			)

	if not kategori or kategori == "Entri Jurnal":
		conditions = ["docstatus = 1"]
		values = {}
		if filters.get("from_date"):
			conditions.append("posting_date >= %(from_date)s")
			values["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			conditions.append("posting_date <= %(to_date)s")
			values["to_date"] = filters["to_date"]
		where_clause = " AND ".join(conditions)
		# ORDER BY + LIMIT di sini mengambil jendela transaksi TERBARU (bukan
		# terlama) -- aman untuk kalkulasi saldo berjalan di
		# _attach_saldo_kas_kecil, karena "opening" balance-nya dihitung dari
		# SUM seluruh GL Entry SEBELUM tanggal baris tertua di jendela ini,
		# bukan diasumsikan 0.
		journal_entries = frappe.db.sql(
			f"""
			SELECT name, posting_date, user_remark, total_debit
			FROM `tabJournal Entry`
			WHERE {where_clause}
			ORDER BY posting_date DESC
			LIMIT 5000
			""",
			values,
			as_dict=1,
		)
		for je in journal_entries:
			rows.append(
				{
					"tanggal": je.posting_date,
					"kategori": "Entri Jurnal",
					"referensi": je.name,
					"keterangan": je.user_remark,
					"nominal": je.total_debit,
					"status": "Tersubmit",
					"saldo": None,
				}
			)

	_attach_saldo_kas_kecil(rows)
	rows.sort(key=lambda r: r["tanggal"], reverse=True)
	return rows


def _attach_saldo_kas_kecil(rows):
	# Format "Laporan Keuangan SAI - Operasional Harian" asli (docs/dokumen
	# asli/) punya kolom SALDO berjalan setelah tiap transaksi. Dihitung dari
	# GL Entry akun Kas Kecil yang benar-benar terpaut ke Journal Entry yang
	# muncul di laporan ini -- bukan dari nominal Petty Cash Entry langsung,
	# supaya tetap akurat kalau nanti ada mutasi Kas Kecil dari sumber lain
	# (top-up manual, dsb).
	company = frappe.defaults.get_global_default("company")
	if not company:
		return

	abbr = frappe.get_cached_value("Company", company, "abbr")
	account = f"Kas Kecil - {abbr}"
	if not frappe.db.exists("Account", account):
		return

	je_rows = [row for row in rows if row["kategori"] == "Entri Jurnal"]
	if not je_rows:
		return
	je_rows.sort(key=lambda r: r["tanggal"])

	je_names = [row["referensi"] for row in je_rows]
	gl_by_voucher = dict(
		frappe.db.sql(
			"""
			SELECT voucher_no, SUM(debit) - SUM(credit)
			FROM `tabGL Entry`
			WHERE account = %s AND voucher_type = 'Journal Entry' AND voucher_no IN %s AND is_cancelled = 0
			GROUP BY voucher_no
			""",
			(account, je_names),
		)
	)

	opening = flt(
		frappe.db.sql(
			"""
			SELECT SUM(debit) - SUM(credit) FROM `tabGL Entry`
			WHERE account = %s AND posting_date < %s AND is_cancelled = 0
			""",
			(account, je_rows[0]["tanggal"]),
		)[0][0]
	)

	running = opening
	for row in je_rows:
		running += flt(gl_by_voucher.get(row["referensi"]))
		row["saldo"] = running
