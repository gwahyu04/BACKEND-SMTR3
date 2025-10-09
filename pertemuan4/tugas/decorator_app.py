from flask import Flask, render_template, redirect, url_for, request, session
from functools import wraps

app = Flask(__name__)
app.secret_key = "pass1234"

# Dekorator untuk memeriksa apakah pengguna sudah login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Halaman Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Contoh validasi sederhana
        if username == 'admin' and password == 'password123':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Username atau Password salah!')

    return render_template('login.html')


# Halaman Dashboard (proteksi login)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# Halaman Logout
@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
