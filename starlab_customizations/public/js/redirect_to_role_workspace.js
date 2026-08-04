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

	// 2026-08-04: request user "sidebar-nya gaperlu ada kalo belum masuk
	// dashboard masing-masing role" -- flash halaman default di atas juga
	// nge-flash sidebar bawaan halaman itu (kosong/isi cuma "Getting
	// Started", bukan menu role yang benar) selama jeda frappe.call ini.
	// frappe.app.sidebar adalah SATU instance yang dipakai ulang lintas
	// route (bukan dibuat baru tiap pindah halaman -- lihat make_sidebar()
	// di desk.js/frappe.Application), jadi wajib di-toggle balik nyala
	// setelah redirect kelar (baik berhasil dapat rute maupun tidak),
	// kalau enggak dia bakal nyangkut ke-hide selamanya.
	function toggle_sidebar(show) {
		if (frappe.app && frappe.app.sidebar) {
			frappe.app.sidebar.toggle(!show);
		}
	}

	$(document).on("app_ready", function () {
		if (frappe.session.user === "Guest") return;
		if (!is_empty_route(frappe.get_route())) return;

		toggle_sidebar(false);

		frappe.call({
			method: "starlab_customizations.install.get_my_workspace_route",
			callback: function (r) {
				if (r.message) {
					frappe.set_route(r.message);
				}
				toggle_sidebar(true);
			},
			error: function () {
				toggle_sidebar(true);
			},
		});
	});
})();
