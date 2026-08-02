import frappe
from frappe.integrations.utils import make_post_request

# TSD Bagian 11 (Integration Design) + Bagian 10 (Notification Design):
# "Pengiriman WhatsApp diteruskan lewat Server Script hook di
# starlab_integrations". Belum ada akun/API key provider WhatsApp asli
# milik SAI (WhatsApp Business API / Twilio / Fonnte) -- send_whatsapp_message
# di bawah ini adalah kerangka siap-pakai: begitu WhatsApp Settings diisi
# kredensial asli, notifikasi lain di project ini (lihat
# notify_via_whatsapp) langsung bisa mengirim tanpa perubahan kode lagi.
#
# Format request per provider mengikuti dokumentasi resmi masing-masing
# per Januari 2026; kredensial & endpoint tetap perlu dikonfirmasi ulang
# oleh yang mendaftarkan akunnya sebelum dipakai produksi.


def send_whatsapp_message(mobile_no: str, message: str) -> bool:
	"""Kirim pesan WhatsApp. Return False (bukan raise) kalau belum
	terkonfigurasi atau gagal -- notifikasi WhatsApp adalah channel
	tambahan, bukan syarat, jadi kegagalannya tidak boleh menghentikan
	proses yang memanggilnya."""
	if not mobile_no:
		return False

	settings = frappe.get_single("WhatsApp Settings")
	if not settings.enabled or not settings.provider or not settings.api_url:
		return False

	api_key = settings.get_password("api_key", raise_exception=False)
	if not api_key:
		return False

	try:
		if settings.provider == "Fonnte":
			make_post_request(
				settings.api_url,
				headers={"Authorization": api_key},
				data={"target": mobile_no, "message": message},
			)
		elif settings.provider == "Twilio":
			make_post_request(
				settings.api_url,
				auth=(settings.sender_number, api_key),
				data={
					"To": f"whatsapp:{mobile_no}",
					"From": f"whatsapp:{settings.sender_number}",
					"Body": message,
				},
			)
		elif settings.provider == "WhatsApp Business API":
			make_post_request(
				settings.api_url,
				headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
				data=frappe.as_json(
					{
						"messaging_product": "whatsapp",
						"to": mobile_no,
						"type": "text",
						"text": {"body": message},
					}
				),
			)
		else:
			# "Custom" -- provider generik lain, format request perlu
			# disesuaikan manual di sini sebelum dipakai.
			make_post_request(
				settings.api_url,
				headers={"Authorization": f"Bearer {api_key}"},
				data={"to": mobile_no, "message": message},
			)
		return True
	except Exception:
		frappe.log_error(title="Gagal mengirim WhatsApp", message=frappe.get_traceback())
		return False


def _notify_role_via_whatsapp(role: str, message: str) -> None:
	"""Logika inti -- dipanggil LANGSUNG (bukan lewat HTTP) oleh kode
	server-side lain (mis. starlab_customizations.tasks._notify_role) yang
	sudah menentukan sendiri role/isi pesannya sebagai bagian dari alur
	bisnis normal (approval pending, SLA, dst.). Nomor tujuan diambil dari
	mobile_no Employee milik user yang pegang role tsb (TSD Bagian 11).
	Tidak ada pengecekan permission di sini dengan sengaja -- pemanggil
	server-side ini sudah trusted by design. Untuk endpoint yang bisa
	dipanggil user dari luar, lihat notify_role_via_whatsapp di bawah."""
	users = frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent")
	if not users:
		return

	mobile_numbers = frappe.get_all(
		"Employee", filters={"user_id": ["in", users]}, pluck="cell_number"
	)
	for mobile_no in mobile_numbers:
		if mobile_no:
			send_whatsapp_message(mobile_no, message)


@frappe.whitelist()
def notify_role_via_whatsapp(role: str, message: str) -> None:
	"""Endpoint HTTP untuk trigger broadcast WhatsApp manual ke seluruh
	pemegang suatu role, dengan role & isi pesan bebas dari pemanggil --
	dibatasi ke role yang memang berwenang broadcast manual, supaya user
	biasa yang sekadar login tidak bisa memicu pengiriman WhatsApp berbayar
	ke role manapun dengan pesan bebas. Notifikasi OTOMATIS dari alur bisnis
	(approval pending, SLA, dst.) tidak lewat sini -- itu memanggil
	_notify_role_via_whatsapp langsung, lihat starlab_customizations.tasks."""
	frappe.only_for(["System Manager", "Direksi", "Manajer Mutu"])
	_notify_role_via_whatsapp(role, message)
