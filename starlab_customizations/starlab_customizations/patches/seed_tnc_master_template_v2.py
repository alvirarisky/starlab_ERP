import frappe

# PRD v8 Sprint 12, item 6: masa berlaku penawaran naik 30 -> 45 hari, dan
# syarat pelunasan naik dari 30 hari menjadi maksimal 7 hari kalender
# setelah invoice terbit (Term of Payment final, dikonfirmasi PO).
#
# Dibuat sebagai VERSI BARU ("02"), bukan menimpa isi versi "01" -- sesuai
# desain TNC Master Template sendiri: Quotation yang sudah terbit tetap
# merujuk versi T&C yang berlaku saat itu (lihat quotation_hooks.py
# ::_set_active_tnc_template), jadi Quotation lama harus tetap menampilkan
# S&K 30/30 hari yang berlaku waktu itu, bukan ikut berubah diam-diam.
# Quotation baru otomatis pakai versi ini begitu berlaku_sejak terlewati.
VERSI = "02"
KONTEN_TNC = """
<ol>
<li>Masa berlaku penawaran adalah 45 hari kalender sejak terbitnya surat ini.</li>
<li>Surat Penawaran yang telah disetujui dan ditandatangani serta diberi stempel oleh pelanggan secara otomatis status hukumnya berubah menjadi Purchasing Order (PO) atau order pembelian jasa pengujian laboratorium dari pelanggan, termasuk jasa untuk pengambilan sample di lokasi yang diminta oleh pelanggan sesuai schedule sampling yang disepakati berdasarkan point nomor 4.</li>
<li>Harga tersebut berdasarkan jumlah sampel yang tercantum dan harga dapat berubah jika ada perubahan jumlah sampel uji terbaru/aktual yang akan menjadi perhitungan dasar penagihan.</li>
<li>Schedule sampling akan dikonfirmasi maksimal 2 (dua) hari kerja setelah PO dan form lampiran A1 kami terima.</li>
<li>Ketentuan terkait pengambilan sampel:
<ol type="a">
<li>Apabila terjadi keterlambatan karena cuaca atau kendala teknis lain (bukan disebabkan oleh PT Starlab Analitik Indonesia), biaya teknisi dan peralatan akan dihitung berdasarkan hari aktual di lapangan.</li>
<li>Apabila terjadi pembatalan pengambilan sampel oleh pelanggan (bukan disebabkan oleh PT Starlab Analitik Indonesia) setelah tim berangkat menuju lokasi, maka seluruh biaya transportasi dan akomodasi yang timbul akan menjadi tanggung jawab pelanggan.</li>
</ol>
</li>
<li>Laporan Hasil Uji (LHU) akan diterima oleh pelanggan, dengan ketentuan sebagai berikut:
<ol type="a">
<li>Pelanggan akan menerima draft Laporan Hasil Uji setelah 10 (sepuluh) hari kerja terhitung setelah sampel diterima dan terdaftar di PT Starlab Analitik Indonesia.</li>
<li>Pelanggan diberikan hak untuk melakukan review, maksimal 3 (tiga) hari kerja setelah draft Laporan Hasil Uji diterima.</li>
<li>Draft Laporan Hasil Uji akan dicetak dan ditandatangani, setelah masa 3 (tiga) hari waktu review.</li>
<li>Laporan Hasil Uji tersedia dalam bentuk softcopy dan hardcopy. Softcopy akan kami kirimkan kepada pelanggan, dan hardcopy dapat diserahkan setelah pelanggan melakukan pembayaran.</li>
</ol>
</li>
<li>Ketentuan mengenai dokumen penagihan:
<ol type="a">
<li>Dokumen penagihan akan dikirimkan setelah pengambilan sample selesai dilakukan. Dokumen tagihan terdiri dari: Penawaran, Purchase Order (PO), Invoice, Kwitansi, Faktur Pajak.</li>
<li>Dokumen-dokumen khusus yang menjadi persyaratan pelanggan dalam proses penagihan, dikirimkan ke perusahaan maksimal 3 (tiga) hari setelah dokumen tagihan diterima.</li>
</ol>
</li>
<li>Syarat dan ketentuan pembayaran:
<ol type="a">
<li>Untuk pemesanan dengan nilai lebih dari sama dengan Rp10.000.000,- diharuskan melakukan pembayaran uang muka (down payment) 50% sebelum pekerjaan dilaksanakan dan pelunasan paling lambat 7 (tujuh) hari kalender setelah invoice diterima oleh pelanggan.</li>
<li>Setiap pembayaran wajib mencantumkan nomor invoice sebagai keterangan pembayaran dan mengirimkan bukti pembayaran. Pembayaran dapat dilakukan melalui transfer rekening Bank Mandiri atas nama PT Starlab Analitik Indonesia.</li>
</ol>
</li>
<li>Ketentuan tentang faktur pajak dan PPH 23:
<ol type="a">
<li>Permintaan revisi faktur pajak dapat dilakukan maksimal pada tanggal 10 pada bulan berikutnya. Permintaan revisi faktur pajak di atas tanggal tersebut tidak akan dilayani.</li>
<li>Bukti potong PPH 23 dapat dikirimkan oleh pelanggan maksimal 3 hari setelah pembayaran.</li>
</ol>
</li>
<li>Penerimaan sampel dapat dilakukan dari Senin s/d Jumat sejak pukul 08.00 s/d 15.30 WIB.</li>
<li>Sampel sisa pengujian (apabila ada) akan disimpan paling lama 1 (satu) bulan, dan setelah itu akan dimusnahkan.</li>
<li>Penawaran ini bersifat final, pembatalan Purchasing Order (PO) maksimal dilakukan H-2 dari jadwal yang sudah ditetapkan. Sedangkan, apabila pembatalan dilakukan H-1 dan telah melakukan pembayaran uang muka, maka uang muka tersebut dianggap hangus.</li>
</ol>
"""


def execute():
	if frappe.db.exists("TNC Master Template", {"versi_template": VERSI}):
		return

	frappe.get_doc(
		{
			"doctype": "TNC Master Template",
			"versi_template": VERSI,
			"berlaku_sejak": frappe.utils.nowdate(),
			"konten_tnc": KONTEN_TNC,
		}
	).insert(ignore_permissions=True)
