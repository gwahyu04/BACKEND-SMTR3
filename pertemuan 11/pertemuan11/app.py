from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "uploads")

# ==== FORMAT RUPIAH ====
@app.template_filter("rupiah")
def format_rupiah(angka):
    try:
        return "Rp {:,}".format(int(float(angka))).replace(",", ".")
    except:
        return "Rp 0"

# ==== FOLDER UPLOAD ====
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# ==== DATABASE ====
def get_db():
    conn = sqlite3.connect("stokumkm.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rental(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_mobil TEXT,
            merk TEXT,
            harga_sewa REAL,
            status TEXT,
            foto TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ================= FRONTEND =================

@app.route("/")
def beranda():
    return render_template("frontend/beranda.html")

@app.route("/armada")
def armada():
    conn = get_db()
    data = conn.execute(
        "SELECT * FROM rental WHERE status='Tersedia'"
    ).fetchall()
    conn.close()
    return render_template("frontend/armada.html", armada=data)

@app.route("/tentang")
def tentang():
    return render_template("frontend/tentang.html")

@app.route("/kontak")
def kontak():
    return render_template("frontend/kontak.html")

# ================= ADMIN =================

@app.route("/admin")
def admin_index():
    conn = get_db()
    rows = conn.execute("SELECT * FROM rental").fetchall()
    conn.close()
    return render_template("admin/index.html", stoks=rows)

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if request.method == "POST":
        file = request.files["foto"]
        filename = file.filename if file.filename else None

        if filename:
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = get_db()
        conn.execute("""
            INSERT INTO rental (nama_mobil, merk, harga_sewa, status, foto)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.form["nama_mobil"],
            request.form["merk"],
            request.form["harga_sewa"],
            request.form["status"],
            filename
        ))
        conn.commit()
        conn.close()

        return redirect(url_for("admin_index"))

    return render_template("admin/add.html")

@app.route("/admin/edit/<int:id>", methods=["GET", "POST"])
def admin_edit(id):
    conn = get_db()
    stok = conn.execute("SELECT * FROM rental WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        file = request.files["foto"]
        filename = stok["foto"]

        if file and file.filename:
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn.execute("""
            UPDATE rental
            SET nama_mobil=?, merk=?, harga_sewa=?, status=?, foto=?
            WHERE id=?
        """, (
            request.form["nama_mobil"],
            request.form["merk"],
            request.form["harga_sewa"],
            request.form["status"],
            filename,
            id
        ))
        conn.commit()
        conn.close()

        return redirect(url_for("admin_index"))

    conn.close()
    return render_template("admin/edit.html", stok=stok)

@app.route("/admin/delete/<int:id>")
def admin_delete(id):
    conn = get_db()
    foto = conn.execute(
        "SELECT foto FROM rental WHERE id=?", (id,)
    ).fetchone()

    if foto and foto["foto"]:
        path = os.path.join(app.config["UPLOAD_FOLDER"], foto["foto"])
        if os.path.exists(path):
            os.remove(path)

    conn.execute("DELETE FROM rental WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_index"))

# ==== RUN ====
if __name__ == "__main__":
    app.run(debug=True)
