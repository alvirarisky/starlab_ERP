import frappe

PRINT_FORMAT_NAME = "LHU Resmi"

HTML = """
<div style="font-family: Arial, sans-serif; font-size: 12px;">
  <table style="width: 100%; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 12px;">
    <tr>
      <td style="width: 70%; vertical-align: middle;">
        <div style="font-size: 18px; font-weight: bold;">PT STARLAB ANALITIK INDONESIA</div>
        <div style="font-size: 11px;">Laboratorium Pengujian Terakreditasi ISO/IEC 17025</div>
        <div style="font-size: 10px;">Jl. Contoh Alamat Placeholder No. 123, Kota, Indonesia &mdash; (021) 000-0000</div>
      </td>
      <td style="width: 30%; text-align: right; vertical-align: middle; font-size: 10px; color: #888;">
        [LOGO PLACEHOLDER]
      </td>
    </tr>
  </table>

  <div style="text-align: center; font-weight: bold; font-size: 14px; text-decoration: underline; margin-bottom: 12px;">
    LAPORAN HASIL UJI (LHU)
  </div>

  <table style="width: 100%; margin-bottom: 12px;">
    <tr>
      <td style="width: 20%;">Nomor LHU</td>
      <td style="width: 2%;">:</td>
      <td style="width: 28%;">{{ doc.name }}</td>
      <td style="width: 20%;">Tanggal Terbit</td>
      <td style="width: 2%;">:</td>
      <td style="width: 28%;">{{ frappe.utils.formatdate(doc.tanggal_terbit) }}</td>
    </tr>
    <tr>
      <td>Customer</td>
      <td>:</td>
      <td>{{ doc.customer }}</td>
      <td>Work Order</td>
      <td>:</td>
      <td>{{ doc.work_order }}</td>
    </tr>
    <tr>
      <td>Diterbitkan Oleh</td>
      <td>:</td>
      <td>{{ doc.diterbitkan_oleh }}</td>
      <td>Status</td>
      <td>:</td>
      <td>{{ doc.status }}</td>
    </tr>
  </table>

  <table style="width: 100%; border-collapse: collapse;" border="1" cellpadding="4">
    <thead>
      <tr style="background-color: #f0f0f0;">
        <th>No</th>
        <th>Parameter</th>
        <th>Hasil Uji</th>
        <th>Satuan</th>
        <th>Metode Acuan</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.test_result_list %}
      <tr>
        <td style="text-align: center;">{{ loop.index }}</td>
        <td>{{ row.parameter }}</td>
        <td style="text-align: right;">{{ row.hasil_uji }}</td>
        <td>{{ row.satuan }}</td>
        <td>{{ row.metode_acuan or "-" }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table style="width: 100%; margin-top: 40px;">
    <tr>
      <td style="width: 60%;"></td>
      <td style="width: 40%; text-align: center;">
        Kota Placeholder, {{ frappe.utils.formatdate(doc.tanggal_terbit) }}<br><br><br><br>
        <div style="border-top: 1px solid #000; display: inline-block; padding-top: 4px;">
          {{ doc.diterbitkan_oleh }}
        </div>
      </td>
    </tr>
  </table>

  <div style="margin-top: 16px; font-size: 9px; color: #888; border-top: 1px solid #ccc; padding-top: 4px;">
    Dokumen ini merupakan Laporan Hasil Uji resmi PT Starlab Analitik Indonesia. Kop surat, logo, dan alamat pada
    dokumen ini masih berupa placeholder Fase 2 dan akan dilengkapi pada sprint resmi.
  </div>
</div>
"""


def execute():
	if frappe.db.exists("Print Format", PRINT_FORMAT_NAME):
		doc = frappe.get_doc("Print Format", PRINT_FORMAT_NAME)
		doc.html = HTML
		doc.save(ignore_permissions=True)
		print(f"Print Format '{PRINT_FORMAT_NAME}' already existed, HTML updated.")
	else:
		doc = frappe.get_doc({
			"doctype": "Print Format",
			"name": PRINT_FORMAT_NAME,
			"doc_type": "LHU",
			"module": "Starlab Lab Ops",
			"print_format_type": "Jinja",
			"standard": "Yes",
			"disabled": 0,
			"html": HTML,
		})
		doc.insert(ignore_permissions=True)
		print(f"Print Format '{PRINT_FORMAT_NAME}' created.")
	frappe.db.commit()
