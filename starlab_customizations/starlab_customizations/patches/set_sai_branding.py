import frappe

# Polish tampilan Client Dashboard + branding dasar: samakan App Logo/Favicon
# Desk & website dengan logo resmi PT Starlab Analitik Indonesia
# (docs/dokumen asli/SAI Logo_name.png), dan set warna primer website supaya
# tombol/aksen konsisten dengan warna brand (cyan #11A8E0), bukan biru
# default Bootstrap. Aset logo di-crop jadi "mark" (ikon bintang + LAB, tanpa
# nama perusahaan) supaya tetap jelas dipakai kecil di navbar/favicon --
# dibundel sebagai asset statis app (public/images/), bukan File doctype,
# karena ini aset branding tetap milik kode, bukan data yang di-upload user.
SAI_CYAN = "#11A8E0"
SAI_CYAN_HOVER = "#0D89B7"
APP_LOGO_PATH = "/assets/starlab_customizations/images/sai-logo.png"
FAVICON_PATH = "/assets/starlab_customizations/images/sai-favicon.png"
WEBSITE_THEME_NAME = "PT Starlab Analitik Indonesia"

# Frappe's newer "espresso" design system styles .btn-primary from a fixed
# --btn-primary token (--surface-gray-10, near-black -- see
# frappe/public/css/espresso/legacy.css) that is NOT driven by Website
# Theme.primary_color at all -- confirmed by inspecting the compiled SCSS
# output (`$primary` correctly resolves to our color, but nothing in the
# espresso button component actually reads it). custom_scss is the
# documented escape hatch for exactly this (rendered after all imports in
# website_theme_template.scss, so it wins the cascade) -- needed to make
# "tombol dan aksen" actually reflect the brand color as asked, not just
# the legacy $primary/--primary variable which most current components
# ignore.
CUSTOM_SCSS_OVERRIDE = f"""
:root {{
	--btn-primary: {SAI_CYAN};
}}
.btn-primary {{
	background-color: {SAI_CYAN} !important;
	border-color: {SAI_CYAN} !important;
}}
.btn-primary:hover,
.btn-primary:focus {{
	background-color: {SAI_CYAN_HOVER} !important;
	border-color: {SAI_CYAN_HOVER} !important;
}}
"""


def execute():
	_set_website_settings_logo()
	_set_primary_color()


def _set_website_settings_logo():
	website_settings = frappe.get_single("Website Settings")
	website_settings.app_logo = APP_LOGO_PATH
	website_settings.favicon = FAVICON_PATH
	website_settings.save(ignore_permissions=True)


def _set_primary_color():
	if not frappe.db.exists("Color", SAI_CYAN):
		frappe.get_doc({"doctype": "Color", "name": SAI_CYAN, "color": SAI_CYAN}).insert(
			ignore_permissions=True
		)

	if frappe.db.exists("Website Theme", WEBSITE_THEME_NAME):
		theme = frappe.get_doc("Website Theme", WEBSITE_THEME_NAME)
	else:
		theme = frappe.get_doc(
			{
				"doctype": "Website Theme",
				"theme": WEBSITE_THEME_NAME,
				"module": "Website",
				"custom": 1,
			}
		)
	theme.primary_color = SAI_CYAN
	theme.custom_scss = CUSTOM_SCSS_OVERRIDE
	theme.save(ignore_permissions=True)

	website_settings = frappe.get_single("Website Settings")
	website_settings.website_theme = WEBSITE_THEME_NAME
	website_settings.save(ignore_permissions=True)
