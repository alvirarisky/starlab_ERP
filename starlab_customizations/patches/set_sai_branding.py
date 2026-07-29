import frappe

# Polish tampilan Client Dashboard + branding dasar: samakan App Logo/Favicon
# Desk & website dengan logo resmi PT Starlab Analitik Indonesia
# (docs/dokumen asli/SAI Logo_name.png), dan set warna primer website supaya
# tombol/aksen konsisten dengan warna brand (cyan #11A8E0), bukan biru
# default Bootstrap. Aset logo di-crop jadi "mark" (ikon bintang + LAB, tanpa
# nama perusahaan) supaya tetap jelas dipakai kecil di navbar/favicon --
# dibundel sebagai asset statis app (public/images/), bukan File doctype,
# karena ini aset branding tetap milik kode, bukan data yang di-upload user.
APP_LOGO_PATH = "/assets/starlab_customizations/images/sai-logo.png"
FAVICON_PATH = "/assets/starlab_customizations/images/sai-favicon.png"

# NOTE: patch ini sudah ter-eksekusi (patches tidak re-run) -- bagian
# "set warna primer via Website Theme custom_scss" yang tadinya ada di
# sini SUDAH DIHAPUS dari kode karena ternyata memicu bug kompilasi
# @import .css di Frappe versi ini (~25 asset 500 di setiap halaman
# website -- lihat patches/fix_sai_branding_css_import.py buat detail
# lengkap + revert-nya). Warna tombol brand sekarang di-set lewat static
# CSS biasa (public/css/starlab_branding.css via web_include_css),
# sepenuhnya di luar patch ini. App Logo/Favicon di bawah TETAP valid,
# tidak kena masalah yang sama.


def execute():
	_set_website_settings_logo()


def _set_website_settings_logo():
	website_settings = frappe.get_single("Website Settings")
	website_settings.app_logo = APP_LOGO_PATH
	website_settings.favicon = FAVICON_PATH
	website_settings.save(ignore_permissions=True)
