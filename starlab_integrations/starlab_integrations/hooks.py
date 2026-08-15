app_name = "starlab_integrations"
app_title = "Starlab Integrations"
app_publisher = "PT Starlab Analitik Indonesia"
app_description = "Modul integrasi WhatsApp Gateway dan Client Portal SAI"
app_email = "banyugong3@gmail.com"
app_license = "mit"

# Send non-GET requests for this app's endpoints as native `application/json`
# bodies instead of form-encoded, per-key JSON-stringified values.
use_json_request_body = True

# LHU (dipakai halaman /status-klien) dimiliki starlab_lab_ops.
required_apps = ["starlab_lab_ops"]

# Portal
# ------

# TSD Bagian 9: Client Portal -- status LHU & Invoice untuk klien, muncul di
# sidebar portal Customer di samping menu native ERPNext (Orders, Invoices).
standard_portal_menu_items = [
	{"title": "Status LHU & Invoice", "route": "/status-klien", "role": "Customer"},
]

# starlab_integrations app terakhir yang di-install (lihat docker/start.sh) --
# lihat komentar di seed_test_users.py buat alasan lengkap kenapa seed akun
# test per-role hidup di sini, bukan di app yang lebih "cocok" isinya.
after_install = "starlab_integrations.seed_test_users.after_install"

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# Require all whitelisted methods to have type annotations
require_type_annotated_api_methods = True
