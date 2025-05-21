from flask import Flask, request, jsonify
import pdfkit
import tempfile
import os

app = Flask(__name__)

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    data = request.get_json()
    html = data.get("html")
    filename = data.get("filename", "offerte.pdf")

    if not html:
        return jsonify({"error": "No HTML provided"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_html:
        temp_html.write(html.encode("utf-8"))
        html_path = temp_html.name

    output_path = f"/tmp/{filename}"

    try:
        pdfkit.from_file(html_path, output_path, options={
            'enable-local-file-access': '',
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'margin-right': '20mm'
        })
        return jsonify({"download_url": f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route(f"/<path:filename>", methods=["GET"])
def serve_pdf(filename):
    pdf_path = f"/tmp/{filename}"
    if os.path.exists(pdf_path):
        return open(pdf_path, 'rb').read(), 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'inline; filename="{filename}"'
        }
    return "Bestand niet gevonden", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
