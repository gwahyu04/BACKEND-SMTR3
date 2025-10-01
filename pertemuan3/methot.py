from flask import Flask, jsonify, Request, make_response
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    data = [{
        'nama'  : 'CV.Rugi terus',
        'lokasi': 'Perum Jlan tanjangan 88 Banyuwangi',
        'aktivitas' : 'Software Development'
    }]
    return make_response(jsonify({'data' : data}), 200)

if __name__ -- '__main__':
    app.run(debug=True)