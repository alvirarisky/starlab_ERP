import frappe
from frappe.tests import IntegrationTestCase

from starlab_customizations.starlab_customizations.tests.quotation_test_utils import make_quotation
from starlab_integrations.tracking import track_order

# Kata kunci yang menandakan data harga/finansial -- endpoint ini (PRD v8
# Bagian 5.7 / TSD Bab 11) SENGAJA tidak pernah boleh mengembalikan salah
# satu dari ini ke guest anonim.
PRICE_RELATED_KEYWORDS = (
	"sub_total", "dpp", "ppn", "total_invoice", "harga", "biaya_kirim",
	"discount", "rush_fee", "grand_total", "net_total", "outstanding_amount",
)


def _find_price_related_keys(value, path=""):
	found = []
	if isinstance(value, dict):
		for key, val in value.items():
			key_lower = str(key).lower()
			if any(kw in key_lower for kw in PRICE_RELATED_KEYWORDS):
				found.append(f"{path}.{key}" if path else key)
			found.extend(_find_price_related_keys(val, f"{path}.{key}" if path else key))
	elif isinstance(value, list):
		for i, item in enumerate(value):
			found.extend(_find_price_related_keys(item, f"{path}[{i}]"))
	return found


class IntegrationTestTrackOrder(IntegrationTestCase):
	"""PRD v8 Bagian 5.7 / TSD Bab 11 -- Client Dashboard tanpa login:
	track_order() harus bisa diakses guest, tidak pernah membocorkan data
	harga/finansial, dan rate-limiting benar-benar membatasi permintaan
	beruntun."""

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_guest_can_access_without_login(self):
		# is_whitelisted adalah pemeriksaan yang sama persis dipakai
		# frappe.handler untuk request HTTP nyata -- memvalidasi
		# allow_guest=True di frappe.whitelist tanpa perlu test client HTTP.
		frappe.set_user("Guest")
		frappe.is_whitelisted(track_order)  # tidak boleh raise PermissionError

		result = track_order("NOMOR-YANG-TIDAK-ADA")
		self.assertEqual(result, {"found": False})

	def test_not_found_returns_false(self):
		result = track_order("NOMOR-YANG-TIDAK-ADA-SAMA-SEKALI")
		self.assertEqual(result, {"found": False})

	def test_response_has_no_price_or_financial_fields(self):
		quotation = make_quotation()
		result = track_order(quotation.name)

		self.assertTrue(result["found"])
		leaked = _find_price_related_keys(result)
		self.assertEqual(leaked, [], f"Field harga/finansial bocor ke response guest: {leaked}")

	def test_rate_limit_blocks_after_threshold(self):
		# @rate_limit di tracking.py hanya aktif kalau frappe.request truthy
		# (lihat frappe.rate_limiter.rate_limit -- no-op di luar konteks
		# request HTTP asli), jadi disimulasikan di sini.
		try:
			original_request = frappe.local.request
			had_request = True
		except AttributeError:
			original_request = None
			had_request = False

		try:
			frappe.local.request = object()
			frappe.local.request_ip = "127.0.0.1"

			for _ in range(30):
				track_order("NOMOR-RATE-LIMIT-TEST")

			with self.assertRaises(frappe.RateLimitExceededError):
				track_order("NOMOR-RATE-LIMIT-TEST")
		finally:
			cache_key = frappe.cache.make_key(f"rl:{frappe.form_dict.cmd}:127.0.0.1") + b":60"
			frappe.cache.delete(cache_key)
			if had_request:
				frappe.local.request = original_request
			else:
				del frappe.local.request
