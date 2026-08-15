(function () {
	// hooks.py::app_include_js -- install.py::get_home_page cuma dipakai
	// Frappe core untuk redirect SEKALI seusai submit form /login. Kalau
	// session masih aktif (cookie belum di-clear) dan user buka /app atau
	// /desk langsung (bukmark, ketik URL, tab baru, REFRESH) tanpa lewat
	// form login lagi, redirect itu tidak pernah kepanggil -- Desk cuma
	// nampilin Workspace publik default (rute kosong) apa adanya. Skrip ini
	// menutup celah itu: tiap Desk baru selesai boot (app_ready, SETELAH
	// frappe.Application.set_route() jalan -- lihat desk.js), kalau rute
	// yang ke-resolve ternyata kosong (persis kondisi "masuk ke /desk
	// generik" yang dikeluhkan), minta rute Workspace role user ke server
	// dan pindah ke situ. Ada jeda render sekilas (flash) ke halaman default
	// dulu sebelum redirect -- tidak ada hook resmi Frappe untuk intercept
	// SEBELUM set_route() pertama jalan tanpa monkey-patch core.
	//
	// 2026-08-15: deteksi "rute kosong" TIDAK BOLEH pakai frappe.get_route()
	// -- dikonfirmasi lewat spy langsung ke frappe.set_route()/localStorage
	// (bukan tebakan): pada fresh full page load ke route SPESIFIK apa pun
	// (bukan cuma /desk polos -- termasuk /app/quotation, /app/customer,
	// Page baru manapun), frappe.router.route() bisa masih nunggu fetch
	// metadata route yang belum ke-cache di localStorage["page_info"]
	// (selalu kosong di awal sesi baru) SAAT app_ready ditrigger (keduanya
	// dipanggil sinkron berurutan di Application.startup(), lihat desk.js) --
	// jadi frappe.get_route() KELIHATAN kosong sesaat meski URL yang diminta
	// browser sudah jelas & valid, bikin skrip ini salah redirect ke
	// Workspace role padahal user sedang menuju halaman spesifik. Baca
	// window.location.pathname langsung sebagai gantinya -- itu SELALU
	// tersedia instan (bagian dari objek `location` browser, tidak
	// bergantung resolusi async apa pun milik Frappe).
	function is_empty_route() {
		var path = window.location.pathname.replace(/^\/(app|desk)\/?/, "");
		return !path;
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
	//
	// PENTING: cek .wrapper eksplisit, bukan cuma .sidebar. Constructor
	// Sidebar (frappe/public/js/frappe/ui/sidebar/sidebar.js) return LEBIH
	// AWAL tanpa pernah bikin this.wrapper kalau frappe.boot.setup_complete
	// falsy -- kejadian ini di instance kita karena Setup Wizard sengaja
	// di-skip (lihat _ensure_setup_complete di install.py, yang sekarang
	// menandai setup complete supaya .wrapper beneran kebentuk). Tanpa cek
	// ini, .toggle() manggil this.wrapper.hide() pas wrapper masih
	// undefined -> TypeError uncaught -> sisa proses boot Desk ikut macet
	// (persis keluhan "gak bisa klik apa-apa" / "putih kosong" / "gak bisa
	// logout" yang dilaporkan). Backend fix di atas menutup akar masalahnya,
	// tapi cek ini tetap dipertahankan sebagai jaring pengaman kalau ada
	// device yang boot info browsernya belum ke-refresh.
	function toggle_sidebar(show) {
		if (frappe.app && frappe.app.sidebar && frappe.app.sidebar.wrapper) {
			frappe.app.sidebar.toggle(!show);
		}
	}

	$(document).on("app_ready", function () {
		if (frappe.session.user === "Guest") return;
		if (!is_empty_route()) return;

		toggle_sidebar(false);

		frappe.call({
			method: "starlab_customizations.install.get_my_workspace_route",
			callback: function (r) {
				// 2026-08-04: install.py::get_home_page() balikin None untuk
				// Administrator (dan siapa pun yang role-nya gak ada di
				// ROLE_HOME_WORKSPACE) DENGAN SENGAJA -- bukan error, itu
				// perilaku yang benar (lihat komentar di install.py). Tapi
				// sebelumnya toggle_sidebar(true) di sini dipanggil TANPA
				// SYARAT, jadi sidebar tetap dimunculin lagi walau redirect-nya
				// gak kejadian -- persis keluhan "sidebar masih ada di halaman
				// desktop [generik]". Sidebar cuma boleh nyala kalau kita
				// BENERAN pindah ke Workspace role, bukan kalau tetap di rute
				// kosong tanpa tujuan.
				if (r.message) {
					frappe.set_route(r.message);
					toggle_sidebar(true);
				}
			},
			error: function () {
				toggle_sidebar(true);
			},
		});
	});
})();
