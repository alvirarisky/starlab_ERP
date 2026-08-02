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
	$(document).on("app_ready", function () {
		if (frappe.session.user === "Guest") return;
		if (frappe.get_route().length !== 0) return;

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
