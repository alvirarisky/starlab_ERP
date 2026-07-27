no_cache = 1


def get_context(context):
	# PRD v8 Bagian 5.7 / TSD Bab 11: halaman publik, TIDAK ada pengecekan
	# login sama sekali (beda dari /status-klien yang berbasis Portal User)
	# -- hasil tracking di-fetch client-side lewat
	# starlab_integrations.tracking.track_order (allow_guest=True).
	context.parents = [{"name": "Home", "route": "/"}]
	return context
