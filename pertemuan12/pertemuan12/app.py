from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS barang (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_barang TEXT,
            nama_barang TEXT,
            harga INTEGER,
            jumlah INTEGER,
            gambar TEXT
        )
    """)
    conn.commit()
    conn.close()

# ================= ROUTES =================
@app.route('/')
def index():
    conn = get_db()
    data = conn.execute("SELECT * FROM barang").fetchall()
    conn.close()
    return render_template('index.html', data=data)

@app.route('/tambah', methods=['POST'])
def tambah():
    kode = request.form['kode']
    nama = request.form['nama']
    harga = request.form['harga']
    jumlah = request.form['jumlah']
    file = request.files['gambar']

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = get_db()
    conn.execute("""
        INSERT INTO barang (kode_barang, nama_barang, harga, jumlah, gambar)
        VALUES (?,?,?,?,?)
    """, (kode, nama, harga, jumlah, filename))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/hapus/<int:id>')
def hapus(id):
    conn = get_db()
    conn.execute("DELETE FROM barang WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ================= EDIT (FORM.HTML) =================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()

    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        jumlah = request.form['jumlah']
        file = request.files['gambar']

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn.execute("""
                UPDATE barang SET 
                kode_barang=?, nama_barang=?, harga=?, jumlah=?, gambar=?
                WHERE id=?
            """, (kode, nama, harga, jumlah, filename, id))
        else:
            conn.execute("""
                UPDATE barang SET 
                kode_barang=?, nama_barang=?, harga=?, jumlah=?
                WHERE id=?
            """, (kode, nama, harga, jumlah, id))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # GET DATA UNTUK FORM
    barang = conn.execute(
        "SELECT * FROM barang WHERE id=?", (id,)
    ).fetchone()
    conn.close()

    return render_template('form.html', barang=barang)

# ================= RUN =================
if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    init_db()
    app.run(debug=True)
