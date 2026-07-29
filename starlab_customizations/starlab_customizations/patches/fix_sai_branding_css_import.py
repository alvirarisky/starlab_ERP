import frappe

# Bagian 3.24 (set_sai_branding.py) membuat Website Theme custom buat
# override warna tombol -- ternyata Website Theme "custom" di versi Frappe
# ini dikompilasi lewat subprocess Node yang tidak meng-inline @import
# ber-ekstensi .css (perilaku standar Sass, bukan bug di kode kita), dan
# hasil kompilasi disajikan dari /files/website_theme/ -- bukan /assets/ --
# jadi semua @import relatif di dalamnya resolve ke URL yang tidak pernah
# ada, bikin puluhan asset 500 di SETIAP halaman website (dikonfirmasi
# lewat DevTools Network tab langsung). Revert Website Settings.website_theme
# balik ke "Standard" dan buang Website Theme custom yang sekarang tidak
# lagi dipakai -- override tombol dipindah ke static CSS biasa lewat
# web_include_css (lihat public/css/starlab_branding.css), yang sepenuhnya
# menghindari pipeline kompilasi yang bermasalah itu.
WEBSITE_THEME_NAME = "PT Starlab Analitik Indonesia"


def execute():
	website_settings = frappe.get_single("Website Settings")
	if website_settings.website_theme == WEBSITE_THEME_NAME:
		website_settings.website_theme = "Standard"
		website_settings.save(ignore_permissions=True)

	if frappe.db.exists("Website Theme", WEBSITE_THEME_NAME):
		frappe.delete_doc("Website Theme", WEBSITE_THEME_NAME, ignore_permissions=True, force=True)
