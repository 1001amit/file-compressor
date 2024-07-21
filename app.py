from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import zipfile
import os
import gzip
import bz2
import lzma
import tarfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COMPRESSED_FOLDER'] = 'compressed'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx', 'pptx', 'csv', 'mp3', 'mp4', 'avi', 'mov'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['COMPRESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def compress_files_zip(files, compression_type):
    zip_filename = os.path.join(app.config['COMPRESSED_FOLDER'], 'compressed.zip')
    with zipfile.ZipFile(zip_filename, 'w', compression=compression_type) as zipf:
        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            zipf.write(file_path, filename)
    return zip_filename

def compress_files_tar(files, compression_type):
    tar_filename = os.path.join(app.config['COMPRESSED_FOLDER'], f'compressed{compression_type}.tar.{compression_type}')
    with tarfile.open(tar_filename, f'w:{compression_type}') as tarf:
        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            tarf.add(file_path, arcname=filename)
    return tar_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    try:
        uploaded_files = request.files.getlist('files[]')
        compression_format = request.form['compression_format']

        if not uploaded_files or uploaded_files[0].filename == '':
            flash('No files selected for uploading', 'error')
            return redirect(url_for('index'))

        for file in uploaded_files:
            if not allowed_file(file.filename):
                flash('File type not allowed', 'error')
                return redirect(url_for('index'))

        if compression_format == 'zip':
            compression_level = request.form['compression_level']
            compression_types = {
                'ZIP_STORED': zipfile.ZIP_STORED,
                'ZIP_DEFLATED': zipfile.ZIP_DEFLATED,
                'ZIP_BZIP2': zipfile.ZIP_BZIP2,
                'ZIP_LZMA': zipfile.ZIP_LZMA
            }
            zip_filename = compress_files_zip(uploaded_files, compression_types[compression_level])
            return send_file(zip_filename, as_attachment=True)
        
        elif compression_format in ['gz', 'bz2', 'xz']:
            tar_filename = compress_files_tar(uploaded_files, compression_format)
            return send_file(tar_filename, as_attachment=True)

        else:
            flash('Invalid compression format', 'error')
            return redirect(url_for('index'))

    except Exception as e:
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

