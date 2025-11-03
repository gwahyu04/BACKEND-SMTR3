from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
import math

app = Flask(__name__)
app.secret_key = 'secret123'

# Konfigurasi database MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'             # Ganti sesuai username MySQL kamu
app.config['MYSQL_PASSWORD'] = 'harfandi123'  # Ganti sesuai password MySQL kamu
app.config['MYSQL_DB'] = 'crud_upload_db'

#  Perbaikan di sini: gunakan path absolut
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Pastikan folder uploads ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

mysql = MySQL(app)

# Fungsi untuk memeriksa ekstensi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# pagination
@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    # hitung total data
    if search_query:
        cur.execute("SELECT COUNT(*) FROM stok WHERE nama LIKE %s", (f'%{search_query}%',))
    
    else:
        cur.execute("SELECT COUNT(*) FROM stok")
    total_rows = cur.fetchone()[0]
    total_pages = math.ceil(total_rows / per_page)

    # Ambil data berdasarkan pagination dan pencarian
    if search_query:
            cur.execute(""" 
                SELECT * FROM stok 
                WHERE nama LIKE %s LIMIT %s 
                OFFSET %s
            """, (f'%{search_query}%', per_page, offset))
    else:
            cur.execute("SELECT * FROM stok LIMIT %s OFFSET %s", (per_page, offset))
    stoks = cur.fetchall()
    cur.close()

    return render_template('pagination.html', dtstok=stoks, page=page, total_pages=total_pages, search_query=search_query)

# Menampilkan gambar dari folder uploads
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Halaman untuk menambah data
@app.route('/add', methods=['GET', 'POST'])
def add_file():
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO stok (kode, nama, harga, filename) VALUES (%s, %s, %s, %s)",
                (kode, nama, harga, filename)
            )
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('index'))
        else:
            return render_template('add.html', error="Format file tidak didukung!")

    return render_template('add.html')

# Halaman untuk menghapus data
@app.route('/delete/<id>', methods=['GET'])
def delete_file(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT filename FROM stok WHERE kode = %s", (id,))
    file_data = cur.fetchone()
    if file_data:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_data[0]))
        except:
            pass
        cur.execute("DELETE FROM stok WHERE kode = %s", (id,))
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

# Halaman untuk mengedit data
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_file(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stok WHERE kode = %s", (id,))
    file_data = cur.fetchone()

    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        new_file = request.files['file']

        # Jika upload file baru
        if new_file and allowed_file(new_file.filename):
            new_filename = secure_filename(new_file.filename)
            new_file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            # Hapus file lama
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_data[3]))
            except:
                pass
            cur.execute("UPDATE stok SET kode=%s, nama=%s, harga=%s, filename=%s WHERE kode=%s",
                        (kode, nama, harga, new_filename, id))
        else:
            cur.execute("UPDATE stok SET kode=%s, nama=%s, harga=%s WHERE kode=%s",
                        (kode, nama, harga, id))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))

    cur.close()
    return render_template('edit.html', file=file_data)


if __name__ == '__main__':
    app.run(debug=True)
