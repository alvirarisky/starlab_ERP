(function () {
	// hooks.py::web_include_js -- fix supaya login mendarat di Workspace
	// role masing-masing (install.py::get_home_page), bukan balik ke /desk
	// generik. Root cause: mengakses /desk TANPA login diarahkan Frappe
	// core ke /login?redirect-to=%2Fdesk, dan
	// templates/includes/login/login.js baca query string `redirect-to`
	// itu LEBIH PRIORITAS daripada field `home_page` di respons login --
	// jadi begitu submit, balik lagi ke /desk generik. Dicoba dulu pakai
	// hook `before_request` (raise frappe.Redirect) tapi itu HANYA
	// ditangani frappe.website.serve di dalam pipeline render halaman
	// website, bukan di before_request yang jalan lebih awal -- hasilnya
	// malah 301 rusak tanpa header Location. Solusinya harus di sisi
	// client, sebelum user sempat submit form: buang parameter itu kalau
	// targetnya cuma /app atau /desk polos (generik, bukan tujuan
	// spesifik apa pun -- kalau ada tujuan spesifik, mis. deep-link ke
	// /desk/quotation/QUO-001, dibiarkan apa adanya).
	if (window.location.pathname !== "/login") return;

	var params = new URLSearchParams(window.location.search);
	var redirectTo = params.get("redirect-to");
	if (redirectTo === "/app" || redirectTo === "/desk") {
		params.delete("redirect-to");
		var newSearch = params.toString();
		var newUrl = window.location.pathname + (newSearch ? "?" + newSearch : "") + window.location.hash;
		window.history.replaceState(null, "", newUrl);
	}
})();
