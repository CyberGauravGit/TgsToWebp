#!/usr/bin/env python3
"""
TGS to WebP Converter - Render.com Optimized
"""

import os
import uuid
from flask import Flask, render_template_string, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configuration
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/outputs'
ALLOWED_EXTENSIONS = {'tgs'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_tgs_to_webp(input_path, output_path, quality=80, width=512, height=512):
    """
    Convert TGS to WebP using lottie
    """
    try:
        import lottie
        print(f"Converting {input_path} to WebP...")
        
        # Load and convert animation
        animation = lottie.parsers.tgs.parse_tgs(input_path)
        lottie.exporters.export_webp(animation, output_path,
                                    quality=quality,
                                    width=width,
                                    height=height)
        print("Conversion successful!")
        return True
    except Exception as e:
        print(f"Conversion failed: {e}")
        return False

def check_dependencies():
    """Check available dependencies"""
    deps = {'lottie': False, 'Pillow': False}
    
    try:
        import lottie
        deps['lottie'] = True
    except: pass
        
    try:
        from PIL import Image
        deps['Pillow'] = True
    except: pass
        
    return deps

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TGS to WebP Converter</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: white; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); width: 100%; max-width: 600px; overflow: hidden; }
        .header { background: #4a5568; color: white; padding: 25px; text-align: center; }
        .content { padding: 30px; }
        .upload-area { border: 2px dashed #cbd5e0; border-radius: 8px; padding: 40px 20px; text-align: center; margin-bottom: 25px; cursor: pointer; }
        .upload-area:hover { border-color: #667eea; background: #f7fafc; }
        .browse-btn { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
        .file-input { display: none; }
        .selected-file { margin-top: 15px; padding: 10px; background: #edf2f7; border-radius: 6px; }
        .settings { margin-bottom: 25px; }
        .form-group { margin-bottom: 15px; }
        .form-control { width: 100%; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; }
        .convert-btn { background: #48bb78; color: white; border: none; padding: 15px; border-radius: 6px; cursor: pointer; width: 100%; font-size: 16px; }
        .alert { padding: 15px; border-radius: 6px; margin-bottom: 20px; }
        .alert-error { background: #fed7d7; color: #c53030; }
        .alert-success { background: #c6f6d5; color: #276749; }
        .result-container { text-align: center; padding: 30px; }
        .download-btn { background: #667eea; color: white; padding: 15px 30px; border-radius: 6px; text-decoration: none; display: inline-block; margin: 20px 0; }
        .dependencies { background: #f7fafc; padding: 15px; border-radius: 6px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 TGS to WebP Converter</h1>
            <p>Convert Telegram TGS stickers to WebP format</p>
        </div>
        
        <div class="content">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="dependencies">
                <h3>📋 Dependencies Status</h3>
                {% for name, status in dependencies.items() %}
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span>{{ name }}</span>
                    <span style="color: {% if status %}#48bb78{% else %}#e53e3e{% endif %};">
                        {% if status %}✅ Available{% else %}❌ Missing{% endif %}
                    </span>
                </div>
                {% endfor %}
            </div>
            
            {% if not conversion_success %}
            <form method="post" action="/convert" enctype="multipart/form-data">
                <div class="upload-area" onclick="document.getElementById('file').click()">
                    <div style="font-size: 48px; color: #a0aec0; margin-bottom: 15px;">📁</div>
                    <p style="color: #4a5568; margin-bottom: 15px;">Click to select TGS file</p>
                    <button type="button" class="browse-btn">Browse Files</button>
                    <input type="file" id="file" class="file-input" name="file" accept=".tgs" required>
                    <div class="selected-file" id="selected-file">No file selected</div>
                </div>
                
                <div class="settings">
                    <h3>⚙️ Settings</h3>
                    <div class="form-group">
                        <label>Quality (1-100)</label>
                        <input type="number" name="quality" class="form-control" min="1" max="100" value="80">
                    </div>
                    <div class="form-group">
                        <label>Width (pixels)</label>
                        <input type="number" name="width" class="form-control" min="1" value="512">
                    </div>
                    <div class="form-group">
                        <label>Height (pixels)</label>
                        <input type="number" name="height" class="form-control" min="1" value="512">
                    </div>
                </div>
                
                <button type="submit" class="convert-btn">Convert to WebP</button>
            </form>
            {% else %}
            <div class="result-container">
                <div style="font-size: 64px; color: #48bb78; margin-bottom: 20px;">✅</div>
                <h2>Conversion Successful!</h2>
                <p>Your file has been converted to WebP format.</p>
                <a href="/download/{{ file_id }}" class="download-btn">Download WebP File</a>
                <br>
                <a href="/" style="color: #667eea; text-decoration: none; margin-top: 10px; display: inline-block;">Convert Another File</a>
            </div>
            {% endif %}
        </div>
    </div>

    <script>
        document.getElementById('file').addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                document.getElementById('selected-file').textContent = 'Selected: ' + e.target.files[0].name;
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, 
                                dependencies=check_dependencies(),
                                conversion_success=False)

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        flash('Please select a TGS file', 'error')
        return redirect('/')
    
    file = request.files['file']
    if file.filename == '':
        flash('Please select a TGS file', 'error')
        return redirect('/')
    
    if not allowed_file(file.filename):
        flash('Please select a valid .tgs file', 'error')
        return redirect('/')
    
    # Get parameters
    quality = int(request.form.get('quality', 80))
    width = int(request.form.get('width', 512))
    height = int(request.form.get('height', 512))
    
    # Generate file paths
    file_id = str(uuid.uuid4())
    input_filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{input_filename}")
    output_filename = f"{os.path.splitext(input_filename)[0]}.webp"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_{output_filename}")
    
    # Save and convert
    file.save(input_path)
    
    try:
        if convert_tgs_to_webp(input_path, output_path, quality, width, height):
            # Cleanup input file
            if os.path.exists(input_path):
                os.remove(input_path)
            
            return render_template_string(HTML_TEMPLATE,
                                        dependencies=check_dependencies(),
                                        conversion_success=True,
                                        original_filename=input_filename,
                                        webp_filename=output_filename,
                                        file_id=file_id)
        else:
            flash('Conversion failed. Please try another file.', 'error')
            return redirect('/')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect('/')

@app.route('/download/<file_id>')
def download_file(file_id):
    for filename in os.listdir(app.config['OUTPUT_FOLDER']):
        if filename.startswith(file_id):
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            if os.path.exists(file_path):
                response = send_file(file_path, as_attachment=True)
                
                # Cleanup after download
                import threading
                def cleanup():
                    import time
                    time.sleep(10)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                threading.Thread(target=cleanup).start()
                return response
    
    flash('File not found', 'error')
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
