from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__)
app.secret_key = 'secret123'

# CONFIG MYSQL - sesuaikan jika perlu
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'qwerty'
app.config['MYSQL_DB'] = 'crud_upload_db'

# Upload config
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# pastikan folder uploads ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default

@app.route('/')
def index():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM stok")
        data = cur.fetchall()
        cur.close()
        return render_template('index.html', file=data)
    except Exception as e:
        print("ERROR index:", e)
        traceback.print_exc()
        return "Terjadi error saat mengambil data. Cek terminal."

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add', methods=['GET', 'POST'])
def add_file():
    if request.method == 'POST':
        try:
            kode = request.form.get('kode', '').strip()
            nama = request.form.get('nama', '').strip()
            harga_raw = request.form.get('harga', '').strip()
            harga = safe_int(harga_raw)

            uploaded = request.files.get('file', None)
            filename = None

            if uploaded and uploaded.filename != '':
                if allowed_file(uploaded.filename):
                    filename = secure_filename(uploaded.filename)
                    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    uploaded.save(save_path)
                else:
                    flash("Ekstensi file tidak diizinkan.")
                    return redirect(url_for('add_file'))

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO stok (kode, nama, harga, filename) VALUES (%s, %s, %s, %s)",
                        (kode or None, nama or None, harga, filename))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('index'))
        except Exception as e:
            print("ERROR add_file:", e)
            traceback.print_exc()
            flash("Terjadi error saat menambah data. Cek terminal.")
            return redirect(url_for('add_file'))

    return render_template('add.html')

@app.route('/delete/<id>', methods=['GET'])
def delete_file(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT filename FROM stok WHERE kode = %s", (id,))
        file_data = cur.fetchone()

        if file_data and file_data[0]:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[0])
            if os.path.exists(file_path):
                os.remove(file_path)

        cur.execute("DELETE FROM stok WHERE kode = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    except Exception as e:
        print("ERROR delete_file:", e)
        traceback.print_exc()
        return "Terjadi error saat menghapus. Cek terminal."

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_file(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM stok WHERE kode = %s", (id,))
        file_data = cur.fetchone()
    except Exception as e:
        print("ERROR fetch edit:", e)
        traceback.print_exc()
        return "Error fetch data."

    if request.method == 'POST':
        try:
            kode = request.form.get('kode', '').strip()
            nama = request.form.get('nama', '').strip()
            harga_raw = request.form.get('harga', '').strip()
            harga = safe_int(harga_raw)
            new_file = request.files.get('file', None)

            if new_file and new_file.filename != '' and allowed_file(new_file.filename):
                # hapus file lama jika ada
                if file_data and file_data[3]:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[3])
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = secure_filename(new_file.filename)
                new_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cur.execute("UPDATE stok SET kode=%s, nama=%s, harga=%s, filename=%s WHERE kode=%s",
                            (kode or None, nama or None, harga, filename, id))
            else:
                cur.execute("UPDATE stok SET kode=%s, nama=%s, harga=%s WHERE kode=%s",
                            (kode or None, nama or None, harga, id))

            mysql.connection.commit()
            cur.close()
            return redirect(url_for('index'))
        except Exception as e:
            print("ERROR edit_file POST:", e)
            traceback.print_exc()
            flash("Terjadi error saat mengedit. Cek terminal.")
            return redirect(url_for('edit_file', id=id))

    # GET
    return render_template('edit.html', file=file_data)

if __name__ == '__main__':
    app.run(debug=True)
