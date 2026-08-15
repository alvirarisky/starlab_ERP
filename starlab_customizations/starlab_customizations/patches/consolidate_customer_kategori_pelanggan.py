import frappe

# PRD v8 Sprint 12, item 5: field jenis_industri (Data, bebas teks) dan
# kategori_pelanggan (Select, 5 opsi tetap) dikonfirmasi PO sebagai field
# yang SAMA PERSIS -- dikonsolidasikan jadi kategori_pelanggan saja.
# jenis_industri dihapus dari custom_field.json (lihat fixtures/custom_field.json)
# setelah patch ini jalan.
VALID_KATEGORI = {
	"Perusahaan",
	"Individu-Perorangan",
	"Institusi Pemerintah",
	"Universitas-Sekolah",
	"Lain-lain",
}


def execute():
	if not frappe.db.exists("Custom Field", "Customer-jenis_industri"):
		return

	customers = frappe.db.sql(
		"""
		SELECT name, jenis_industri, kategori_pelanggan FROM `tabCustomer`
		WHERE jenis_industri IS NOT NULL AND jenis_industri != ''
		""",
		as_dict=True,
	)

	for row in customers:
		if row.kategori_pelanggan:
			# kategori_pelanggan sudah keisi manual -- jangan ditimpa,
			# cukup catat kalau isinya beda supaya bisa dicek manual.
			if row.kategori_pelanggan != row.jenis_industri:
				frappe.log_error(
					title="Konsolidasi kategori_pelanggan: nilai berbeda, perlu review manual",
					message=(
						f"Customer {row.name}: jenis_industri={row.jenis_industri!r},"
						f" kategori_pelanggan={row.kategori_pelanggan!r} (dibiarkan, tidak ditimpa)"
					),
				)
			continue

		if row.jenis_industri in VALID_KATEGORI:
			frappe.db.set_value("Customer", row.name, "kategori_pelanggan", row.jenis_industri)
		else:
			# Nilai bebas teks yang tidak cocok persis ke salah satu opsi
			# Select -- tidak ditebak otomatis, dicatat untuk isian manual
			# oleh Administrasi supaya tidak salah kategorisasi.
			frappe.log_error(
				title="Konsolidasi kategori_pelanggan: perlu isian manual",
				message=(
					f"Customer {row.name}: jenis_industri={row.jenis_industri!r} tidak cocok ke"
					f" salah satu opsi Kategori Pelanggan yang valid ({sorted(VALID_KATEGORI)});"
					" perlu diisi manual."
				),
			)

	# Fixtures cuma nambah/update, tidak pernah menghapus field yang sudah
	# tidak ada lagi di custom_field.json -- jadi field lama dihapus manual
	# di sini setelah datanya beres dimigrasi di atas.
	frappe.delete_doc("Custom Field", "Customer-jenis_industri", ignore_permissions=True, force=True)
	frappe.db.commit()
