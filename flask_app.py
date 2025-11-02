from flask import Flask, request, render_template_string, send_file
import os, tempfile
from shutil import which
import gzip, zlib, subprocess
from lottie import exporters, parsers

app = Flask(__name__)

def convert_tgs_to_webp(input_path, output_path, quality=80, width=512, height=512):
    lottie_cli = which("lottie_convert.py") or which("lottie_convert")
    if lottie_cli:
        try:
            subprocess.check_call([lottie_cli, input_path, output_path])
            return True
        except:
            pass

    try:
        anim = parsers.tgs.parse_tgs(input_path)
        exporters.export_webp(anim, output_path, quality=quality, width=width, height=height)
        return True
    except:
        return False

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>TGS to WebP Converter</title>
<style>
body { font-family: Arial; padding: 30px; max-width: 500px; margin: auto; }
button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
input { padding: 8px; }
</style>
</head>
<body>
<h2>Telegram TGS to WebP Converter</h2>
<form action="/" method="post" enctype="multipart/form-data">
    <input type="file" name="tgsfile" accept=".tgs" required><br><br>
    <button type="submit">Convert</button>
</form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files["tgsfile"]

        tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".tgs").name
        tmp_out = tmp_in.replace(".tgs", ".webp")

        file.save(tmp_in)

        if convert_tgs_to_webp(tmp_in, tmp_out):
            return send_file(tmp_out, as_attachment=True, download_name=file.filename.replace(".tgs",".webp"))
        else:
            return "Conversion failed. Check dependencies."

    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
