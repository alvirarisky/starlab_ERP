(function () {
	// hooks.py::app_include_js -- install.py::get_home_page cuma dipakai
	// Frappe core untuk redirect SEKALI seusai submit form /login. Kalau
	// session masih aktif (cookie belum di-clear) dan user buka /app atau
	// /desk langsung (bukmark, ketik URL, tab baru) tanpa lewat form login
	// lagi, redirect itu tidak pernah kepanggil -- Desk cuma nampilin
	// Workspace publik default (rute kosong) apa adanya. Skrip ini menutup
	// celah itu: tiap Desk baru selesai boot (app_ready, SETELAH
	// frappe.Application.set_route() jalan -- lihat desk.js), kalau rute
	// yang ke-resolve ternyata kosong (persis kondisi "masuk ke /desk
	// generik" yang dikeluhkan), minta rute Workspace role user ke server
	// dan pindah ke situ. Ada jeda render sekilas (flash) ke halaman default
	// dulu sebelum redirect -- tidak ada hook resmi Frappe untuk intercept
	// SEBELUM set_route() pertama jalan tanpa monkey-patch core.
	//
	// PENTING soal deteksi "rute kosong": frappe.router.parse() menghasilkan
	// `[""]` (array isi SATU string kosong) untuk /desk polos, BUKAN `[]`
	// (array kosong beneran) -- lihat convert_to_standard_route() di
	// frappe/public/js/frappe/router.js, tidak ada satu pun cabang if yang
	// match untuk route[0] === "", jadi balik apa adanya. Cek `.length !== 0`
	// makanya SELALU gagal mendeteksi kondisi ini (route.length konsisten 1,
	// bukan 0) -- redirect jadi TIDAK PERNAH kepanggil sama sekali sebelum
	// perbaikan ini, persis root cause keluhan "sering banget ke /desk dulu".
	function is_empty_route(route) {
		return route.length === 0 || (route.length === 1 && !route[0]);
	}

	$(document).on("app_ready", function () {
		if (frappe.session.user === "Guest") return;
		if (!is_empty_route(frappe.get_route())) return;

		frappe.call({
			method: "starlab_customizations.install.get_my_workspace_route",
			callback: function (r) {
				if (r.message) {
					frappe.set_route(r.message);
				}
			},
		});
	});
})();
