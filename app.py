from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import zipfile
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COMPRESSED_FOLDER'] = 'compressed'
app.config['SECRET_KEY'] = 'supersecretkey'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['COMPRESSED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    try:
        uploaded_files = request.files.getlist('files[]')
        if not uploaded_files or uploaded_files[0].filename == '':
            flash('No files selected for uploading', 'error')
            return redirect(url_for('index'))

        zip_filename = os.path.join(app.config['COMPRESSED_FOLDER'], 'compressed.zip')

        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                zipf.write(file_path, filename)

        return send_file(zip_filename, as_attachment=True)

    except Exception as e:
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
