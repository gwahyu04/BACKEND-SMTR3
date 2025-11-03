from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# Konfigurasi koneksi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'qwerty'
app.config['MYSQL_DB'] = 'db_crud'

mysql = MySQL(app)

# READ - Tampilkan data
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_barang")
    data = cur.fetchall()
    cur.close()  # tutup cursor setelah fetch
    return render_template('index.html', databarang=data)


# CREATE - Tambah data
@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tb_barang (kode, nama, harga) VALUES (%s, %s, %s)", (kode, nama, harga))
        mysql.connection.commit()
        cur.close()  # tutup cursor setelah commit
        return redirect(url_for('index'))

    return render_template('tambah.html')


# UPDATE - Edit data
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']

        cur.execute("UPDATE tb_barang SET kode=%s, nama=%s, harga=%s WHERE kode=%s", (kode, nama, harga, id))
        mysql.connection.commit()
        cur.close()  # tutup cursor setelah update
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM tb_barang WHERE kode=%s", [id])
    data = cur.fetchone()
    cur.close()  # tutup cursor setelah fetch pada GET
    return render_template('edit.html', databarang=data)


# DELETE - Hapus data
@app.route('/hapus/<id>', methods=['GET'])
def hapus(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tb_barang WHERE kode=%s", [id])
    mysql.connection.commit()
    cur.close()  # tutup cursor setelah delete
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
