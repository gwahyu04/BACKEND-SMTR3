from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os
from pymongo import MongoClient

app = Flask(__name__)

# Folder Upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Koneksi MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["db_produk"]
collection = db["products"]


# ================= ROUTE: READ DATA =================
@app.route('/')
def index():
    data = collection.find()
    return render_template("index.html", data=data)



# ================= ROUTE: CREATE DATA =================
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        jumlah = request.form['jumlah']

        filename = ""

        # upload file
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != "":
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        collection.insert_one({
            "kode": kode,
            "nama": nama,
            "harga": harga,
            "jumlah": jumlah,
            "gambar": filename
        })

        return redirect(url_for('index'))

    return render_template('add.html')



# ================= ROUTE: UPDATE DATA =================
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    item = collection.find_one({"_id": ObjectId(id)})

    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        jumlah = request.form['jumlah']

        update_data = {
            "kode": kode,
            "nama": nama,
            "harga": harga,
            "jumlah": jumlah
        }

        # Jika upload gambar baru
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != "":
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                update_data["gambar"] = filename

        collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        return redirect(url_for('index'))

    return render_template("edit.html", item=item)



# ================= ROUTE: DELETE DATA =================
@app.route('/delete/<id>')
def delete(id):
    collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))



# ================= MAIN APP =================
if __name__ == "__main__":
    app.run(debug=True)
