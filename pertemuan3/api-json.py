from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    data = [{
        'nama'    : 'Mr. Sodron',
        'pekerjaan' : 'Web Programmer',
        'pesan'   : 'Menerima Pesanan Pembuatan WEB'
    }]
    return make_response(jsonify({'data': data}), 200)

@app.route('/karyawan', methods=['GET', 'POST', 'PUT', 'DELETE'])
def karyawan():
    try:
        if request.method == 'GET':
            data = [{
                'nama'    : 'Mr. Sodron GET',
                'pekerjaan' : 'Web Programmer',
                'pesan'   : 'Menerima Pesanan Pembuatan WEB'
            }]
        elif request.method == 'POST':
            data = [{
                'nama'    : 'Mr. Sodron POST',
                'pekerjaan' : 'Web Programmer',
                'pesan'   : 'Menerima Pesanan Pembuatan WEB'
            }]
        elif request.method == 'PUT':
            data = [{
                'nama'    : 'Mr. Sodron PUT',
                'pekerjaan' : 'Web Programmer',
                'pesan'   : 'Menerima Pesanan Pembuatan WEB'
            }]
        else:
            data = [{
                'nama'    : 'Mr. Sodron DELETE',
                'pekerjaan' : 'Web Programmer',
                'pesan'   : 'Menerima Pesanan Pembuatan WEB'
            }]
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)
    
    return make_response(jsonify({'data': data}), 200)

if __name__ == '__main__':
    app.run(debug=True)