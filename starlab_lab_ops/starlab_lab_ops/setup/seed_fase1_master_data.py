import frappe

COMPANY = "Starlab Analitik Indonesia"


def _ensure_designation(name):
	if not frappe.db.exists("Designation", name):
		frappe.get_doc({"doctype": "Designation", "designation_name": name}).insert(ignore_permissions=True)


def _ensure_territory(name):
	# Site baru dari `bench new-site` tanpa Setup Wizard tidak otomatis
	# membuat Territory per-negara (itu bagian dari Setup Wizard, bukan
	# `new-site` -- lihat juga catatan Company/Setup Wizard di panduan
	# setup). Tanpa ini, seed_customers() gagal dengan
	# "Could not find Territory: Indonesia" begitu Setup Wizard dilewati.
	if not frappe.db.exists("Territory", name):
		frappe.get_doc({
			"doctype": "Territory",
			"territory_name": name,
			"parent_territory": "All Territories",
			"is_group": 0,
		}).insert(ignore_permissions=True)


def seed_customers():
	_ensure_territory("Indonesia")
	customers = [
		"PT Enviro Jaya Lestari",
		"PT Tirta Bening Nusantara",
		"PT Mega Industri Kimia",
		"CV Sumber Alam Sejahtera",
		"PT Bumi Hijau Konsultan",
	]
	for name in customers:
		if frappe.db.exists("Customer", name):
			continue
		frappe.get_doc({
			"doctype": "Customer",
			"customer_name": name,
			"customer_type": "Company",
			"customer_group": "Commercial",
			"territory": "Indonesia",
		}).insert(ignore_permissions=True)
	print(f"Customers: {frappe.db.count('Customer')}")


def seed_employees():
	roles = [
		("Direksi", "Direksi", "Bambang Sutrisno", "Male", "1975-03-12"),
		("Manajer Mutu (MM)", "Manajer Mutu (MM)", "Siti Rahayu", "Female", "1982-07-20"),
		("Manajer Teknis (MT)", "Manajer Teknis (MT)", "Agus Wijaya", "Male", "1980-11-05"),
		("Analis Laboratorium", "Laboratorium/Analis", "Dewi Kusuma", "Female", "1990-02-14"),
		("Administrasi", "Administrasi", "Rina Marlina", "Female", "1993-09-30"),
		("Finance", "Finance", "Hendra Gunawan", "Male", "1988-05-17"),
		("Marketing", "Marketing", "Fajar Nugroho", "Male", "1991-12-01"),
		# 2026-08-03: pasangan Employee utk role "HR" (lihat starlab_customizations
		# ROLE_HOME_WORKSPACE + seed_test_users.py) -- tanpa ini hr.test@example.com
		# tidak bisa ditautkan ke Employee manapun di Langkah linking akun test.
		("HR", "HR", "Yuni Astuti", "Female", "1987-04-22"),
	]
	for designation, _role_label, full_name, gender, dob in roles:
		_ensure_designation(designation)
		first_name, *rest = full_name.split(" ", 1)
		last_name = rest[0] if rest else ""
		if frappe.db.exists("Employee", {"first_name": first_name, "last_name": last_name, "company": COMPANY}):
			continue
		frappe.get_doc({
			"doctype": "Employee",
			"first_name": first_name,
			"last_name": last_name,
			"gender": gender,
			"date_of_birth": dob,
			"date_of_joining": "2023-01-01",
			"company": COMPANY,
			"designation": designation,
			"status": "Active",
		}).insert(ignore_permissions=True)
	print(f"Employees: {frappe.db.count('Employee')}")


def seed_items():
	items = [
		("REG-001", "Larutan Buffer pH 7", "Litre", 20, 5),
		("REG-002", "Larutan Buffer pH 4", "Litre", 20, 5),
		("REG-003", "Reagen COD Digestion Vial", "Box", 30, 10),
		("REG-004", "Larutan Standar Kalibrasi Multiparameter", "Litre", 15, 5),
		("REG-005", "Membrane Filter 0.45 Micron", "Box", 25, 8),
	]
	for code, name, uom, reorder_qty, reorder_level in items:
		if frappe.db.exists("Item", code):
			continue
		frappe.get_doc({
			"doctype": "Item",
			"item_code": code,
			"item_name": name,
			"item_group": "Consumable",
			"stock_uom": uom,
			"is_stock_item": 1,
			"reorder_levels": [{
				"warehouse": "Stores - SAI",
				"warehouse_reorder_level": reorder_level,
				"warehouse_reorder_qty": reorder_qty,
				"material_request_type": "Purchase",
			}],
		}).insert(ignore_permissions=True)
	print(f"Items: {frappe.db.count('Item')}")


def seed_test_parameters():
	params = [
		("PM2.5 (Particulate Matter)", "Udara Ambien", "PP No. 22 Tahun 2021", "µg/Nm3", 150000),
		("Sulfur Dioksida (SO2)", "Udara Ambien", "PP No. 22 Tahun 2021", "µg/Nm3", 125000),
		("Karbon Monoksida (CO)", "Udara Emisi", "Permen LHK No. 11 Tahun 2021", "mg/Nm3", 175000),
		("pH", "Air Permukaan", "PP No. 22 Tahun 2021", "-", 50000),
		("Chemical Oxygen Demand (COD)", "Air Limbah", "Permen LHK No. 5 Tahun 2014", "mg/L", 100000),
		("Biological Oxygen Demand (BOD)", "Air Limbah", "Permen LHK No. 5 Tahun 2014", "mg/L", 100000),
		("Total Coliform", "Air Bersih", "Permenkes No. 2 Tahun 2023", "MPN/100mL", 120000),
		("Kadmium (Cd)", "Tanah", "SNI 6989.86:2019", "mg/kg", 175000),
		("Merkuri (Hg)", "Sedimen", "SNI 6989.78:2019", "mg/kg", 200000),
		("Tingkat Kebisingan", "Kebisingan", "Kepmen LH No. 48 Tahun 1996", "dBA", 90000),
	]
	for name, matriks, regulasi, satuan, harga in params:
		if frappe.db.exists("Test Parameter", name):
			continue
		frappe.get_doc({
			"doctype": "Test Parameter",
			"parameter_name": name,
			"matriks": matriks,
			"regulasi_acuan": regulasi,
			"satuan": satuan,
			"harga_satuan_default": harga,
			"status": "Aktif",
		}).insert(ignore_permissions=True)
	print(f"Test Parameters: {frappe.db.count('Test Parameter')}")


def execute():
	seed_customers()
	seed_employees()
	seed_items()
	seed_test_parameters()
	frappe.db.commit()
	print("Fase 1 master data seeding done.")
