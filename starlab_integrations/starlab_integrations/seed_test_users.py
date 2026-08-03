import frappe

# 7 akun dev/testing, satu per role, dipakai buat coba-coba/demo tanpa perlu
# bikin user manual di tiap device baru. Sengaja hidup di starlab_integrations
# (bukan starlab_customizations yang punya fixtures/role.json) karena ini app
# TERAKHIR yang di-install (lihat urutan --install-app di docker/start.sh) --
# after_install jalan SEBELUM sync_fixtures app itu sendiri (frappe/installer.py),
# jadi taruh di app manapun sebelum starlab_customizations bakal kepanggil
# sebelum role-role custom itu ada. Taruh di app terakhir = satu-satunya cara
# mastiin semua Role dari app lain sudah pasti ke-sync duluan.
# 2026-08-03: Workspace "Laboratorium" dihapus (digabung ke "LIMS", lihat
# starlab_customizations/install.py::ROLE_HOME_WORKSPACE) -- nama Workspace-nya
# gak lagi sama persis dengan nama role utk kasus ini, jadi butuh pengecualian
# eksplisit di sini juga (lookup di bawah defaultnya asumsi nama Workspace ==
# nama Role, lihat komentar di dalam loop).
DEFAULT_WORKSPACE_OVERRIDE = {
	"Laboratorium": "LIMS",
}

TEST_PASSWORD = "Test@12345"
TEST_USERS = [
	("direksi.test@example.com", "Direksi Test", "Direksi"),
	("marketing.test@example.com", "Marketing Test", "Marketing"),
	("administrasi.test@example.com", "Administrasi Test", "Administrasi"),
	("finance.test@example.com", "Finance Test", "Finance"),
	("laboratorium.test@example.com", "Laboratorium Test", "Laboratorium"),
	("manajerteknis.test@example.com", "Manajer Teknis Test", "Manajer Teknis"),
	("manajermutu.test@example.com", "Manajer Mutu Test", "Manajer Mutu"),
	("hr.test@example.com", "HR Test", "HR"),
]


def after_install():
	# developer_mode adalah penanda instance dev/lokal (docker/start.sh selalu
	# menyalakannya) -- akun test dengan password baku TIDAK BOLEH pernah
	# tersedia di instance produksi.
	if not frappe.conf.get("developer_mode"):
		return

	for email, full_name, role in TEST_USERS:
		if frappe.db.exists("User", email):
			continue

		if not frappe.db.exists("Role", role):
			# Role custom belum ada -- kemungkinan urutan install app berubah
			# dari yang diasumsikan. Lewati saja, jangan gagalkan install.
			frappe.log_error(
				title="seed_test_users: role belum ada",
				message=f"Role '{role}' belum ada saat membuat user test {email}, dilewati.",
			)
			continue

		try:
			user_dict = {
				"doctype": "User",
				"email": email,
				"first_name": full_name,
				"send_welcome_email": 0,
				"new_password": TEST_PASSWORD,
				"roles": [{"role": role}],
			}
			# Nama Workspace per-role biasanya sama persis dengan nama role-nya
			# sendiri (starlab_customizations/starlab_customizations/workspace/),
			# kecuali yang eksplisit di-override di DEFAULT_WORKSPACE_OVERRIDE.
			# Tanpa ini, login jatuh ke grid modul generik alih-alih Workspace
			# role yang bersangkutan -- pernah kejadian di beberapa device.
			workspace_name = DEFAULT_WORKSPACE_OVERRIDE.get(role, role)
			if frappe.db.exists("Workspace", workspace_name):
				user_dict["default_workspace"] = workspace_name
			frappe.get_doc(user_dict).insert(ignore_permissions=True)
		except Exception:
			frappe.log_error(title="seed_test_users: gagal membuat user test")

	frappe.db.commit()
