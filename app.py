from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import zipfile
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COMPRESSED_FOLDER'] = 'compressed'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['COMPRESSED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    uploaded_files = request.files.getlist('files[]')
    zip_filename = os.path.join(app.config['COMPRESSED_FOLDER'], 'compressed.zip')

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in uploaded_files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            zipf.write(file_path, filename)

    return send_file(zip_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
