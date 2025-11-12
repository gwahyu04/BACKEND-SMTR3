from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from datetime import date
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret123'

# ========================
#  KONFIG DATABASE
# ========================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'wahyu'
app.config['MYSQL_PASSWORD'] = 'qwerty'
app.config['MYSQL_DB'] = 'data_armada_trevel'

mysql = MySQL(app)

# ========================
#  KONFIG UPLOAD FOTO
# ========================
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========================
#  HALAMAN UTAMA
# ========================
@app.route('/')
def index():
    return redirect(url_for('mobil'))

# ========================
#  CRUD MOBIL
# ========================
@app.route('/mobil')
def mobil():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM mobil")
    data = cur.fetchall()
    cur.close()
    return render_template('mobil.html', mobil=data)

@app.route('/tambah_mobil', methods=['POST'])
def tambah_mobil():
    nama = request.form['nama_mobil']
    merk = request.form['merk']
    tahun = request.form['tahun']
    harga = request.form['harga']
    status = 'Tersedia'

    foto = request.files['foto']
    filename = None

    if foto and allowed_file(foto.filename):
        filename = secure_filename(foto.filename)
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO mobil (nama_mobil, merk, tahun, harga_sewa, foto, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nama, merk, tahun, harga, filename, status))
    mysql.connection.commit()
    flash('Data mobil berhasil ditambahkan!', 'success')
    return redirect(url_for('mobil'))

@app.route('/hapus_mobil/<int:id>')
def hapus_mobil(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT foto FROM mobil WHERE id = %s", (id,))
    foto = cur.fetchone()

    # Hapus file foto jika ada
    if foto and foto[0]:
        path = os.path.join(app.config['UPLOAD_FOLDER'], foto[0])
        if os.path.exists(path):
            os.remove(path)

    cur.execute("DELETE FROM mobil WHERE id = %s", (id,))
    mysql.connection.commit()
    flash('Data mobil berhasil dihapus!', 'danger')
    return redirect(url_for('mobil'))

# ========================
#  CRUD PELANGGAN
# ========================
@app.route('/pelanggan')
def pelanggan():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pelanggan")
    data = cur.fetchall()
    cur.close()
    return render_template('pelanggan.html', pelanggan=data)

@app.route('/tambah_pelanggan', methods=['POST'])
def tambah_pelanggan():
    nama = request.form['nama']
    alamat = request.form['alamat']
    no_telp = request.form['no_telp']

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO pelanggan (nama, alamat, no_telp)
        VALUES (%s, %s, %s)
    """, (nama, alamat, no_telp))
    mysql.connection.commit()
    flash('Data pelanggan berhasil ditambahkan!', 'success')
    return redirect(url_for('pelanggan'))

# ========================
#  CRUD RENTAL
# ========================
@app.route('/rental')
def rental():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.id, m.nama_mobil, p.nama, r.tanggal_pinjam, 
               r.tanggal_kembali, r.tanggal_dikembalikan, 
               r.total_harga, r.denda, r.status
        FROM rental r
        JOIN mobil m ON r.id_mobil = m.id
        JOIN pelanggan p ON r.id_pelanggan = p.id
    """)
    data = cur.fetchall()

    cur.execute("SELECT id, nama_mobil, harga_sewa FROM mobil WHERE status = 'Tersedia'")
    mobil_data = cur.fetchall()
    cur.close()

    return render_template('rental.html', rental=data, mobil=mobil_data)

@app.route('/tambah_rental', methods=['POST'])
def tambah_rental():
    id_mobil = request.form['id_mobil']
    id_pelanggan = request.form['id_pelanggan']
    tanggal_pinjam = request.form['tanggal_pinjam']
    tanggal_kembali = request.form['tanggal_kembali']
    total_harga = request.form['total_harga']
    status = 'Berjalan'

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO rental (id_mobil, id_pelanggan, tanggal_pinjam, tanggal_kembali, total_harga, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (id_mobil, id_pelanggan, tanggal_pinjam, tanggal_kembali, total_harga, status))

    cur.execute("UPDATE mobil SET status = 'Disewa' WHERE id = %s", (id_mobil,))
    mysql.connection.commit()
    flash('Data rental berhasil ditambahkan!', 'success')
    return redirect(url_for('rental'))

# ========================
#  HALAMAN PENGEMBALIAN
# ========================
@app.route('/pengembalian')
def pengembalian():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.id, m.nama_mobil, p.nama, r.tanggal_pinjam, 
               r.tanggal_kembali, r.total_harga
        FROM rental r
        JOIN mobil m ON r.id_mobil = m.id
        JOIN pelanggan p ON r.id_pelanggan = p.id
        WHERE r.status = 'Berjalan'
    """)
    data = cur.fetchall()
    cur.close()
    return render_template('pengembalian.html', rental=data)

# ========================
#  PROSES PENGEMBALIAN
# ========================
@app.route('/kembalikan/<int:id>', methods=['GET'])
def kembalikan(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_mobil, tanggal_kembali FROM rental WHERE id = %s", (id,))
    rental = cur.fetchone()

    if rental:
        id_mobil = rental[0]
        tanggal_kembali = rental[1]
        tanggal_dikembalikan = date.today()

        denda_per_hari = 50000
        denda = 0
        hari_terlambat = 0

        if tanggal_dikembalikan > tanggal_kembali:
            hari_terlambat = (tanggal_dikembalikan - tanggal_kembali).days
            denda = hari_terlambat * denda_per_hari

        cur.execute("""
            UPDATE rental 
            SET status = 'Selesai', tanggal_dikembalikan = %s, denda = %s
            WHERE id = %s
        """, (tanggal_dikembalikan, denda, id))

        cur.execute("UPDATE mobil SET status = 'Tersedia' WHERE id = %s", (id_mobil,))
        mysql.connection.commit()

        if denda > 0:
            flash(f'Mobil dikembalikan terlambat {hari_terlambat} hari. Denda: Rp {denda:,}', 'warning')
        else:
            flash('Mobil dikembalikan tepat waktu tanpa denda.', 'success')
    else:
        flash('Data rental tidak ditemukan.', 'danger')

    cur.close()
    return redirect(url_for('pengembalian'))

# ========================
#  FILTER FORMAT RUPIAH
# ========================
@app.template_filter('rupiah')
def format_rupiah(value):
    try:
        value = int(value)
        return "Rp {:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"

# ========================
#  RUN APP
# ========================
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
