import frappe

# Open question #3 (jawaban Starlab): notifikasi WhatsApp ke customer DAN
# staff (Marketing, Administrasi, Manajer Teknis, Direksi) begitu sample
# diterima & begitu LHU terbit. starlab_lab_ops TIDAK me-require
# starlab_integrations (WhatsApp adalah channel tambahan, bukan syarat --
# lihat starlab_integrations/whatsapp.py) -- pola try/except + frappe.get_attr
# di bawah sama seperti starlab_customizations.tasks._notify_role_whatsapp,
# supaya kedua hook pemanggil ini tetap no-op aman kalau starlab_integrations
# belum terinstall/terkonfigurasi.

WHATSAPP_STAFF_ROLES = ["Marketing", "Administrasi", "Manajer Teknis", "Direksi"]


def notify_staff_and_customer(customer, staff_message, customer_message):
	for role in WHATSAPP_STAFF_ROLES:
		_safe_notify_role(role, staff_message)
	if customer:
		_safe_notify_customer(customer, customer_message)


def _safe_notify_role(role, message):
	try:
		frappe.get_attr("starlab_integrations.whatsapp._notify_role_via_whatsapp")(role, message)
	except Exception:
		pass


def _safe_notify_customer(customer, message):
	try:
		frappe.get_attr("starlab_integrations.whatsapp._notify_customer_via_whatsapp")(customer, message)
	except Exception:
		pass
