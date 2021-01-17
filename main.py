from flask import *
import requests
from fsp import fsp, dfprint
import json
import sys

app = Flask(__name__)
app.register_blueprint(fsp)

host = 'http://127.0.0.1:8080'
user = 'did:example:3c1yq1k3snydmwwx15enif'
tokens = []

@app.route('/', methods=['POST', 'GET'])
def index():
    partners = 'paypal fidelity goldman'.split()
    if request.method == 'POST':
        print('0. START')
        print()

        data = request.form
        for partner in partners:
            if data.get(partner + '.x'):
                fsp = partner
                break

        path = f'/{fsp}/create'
        data = {'user': user}
        requests.post(host + path, json=data)

        return redirect('/wallet')

    else:
        return render_template('create.html', partners=partners)

@app.route('/duo', methods=['POST'])
def duo():
    global notif
    notif = request.get_json()

    print(f'3. {user} stores info required by {notif["fsp"]}')
    print(notif)
    print()

    return ''

@app.route('/wallet', methods=['POST', 'GET'])
def wallet():
    global notif
    if request.method == 'POST':
        data = request.form
        dtypes = data.getlist('token')

        if dtypes:
            print(f'4. {user} issues {dtypes} tokens to {notif["fsp"]}')
            print()

            data = [
                token for token in tokens
                if token['dtype'] in dtypes
            ]

            path = host + f'/{notif["fsp"]}/auth'
            requests.post(path, json=data)

        return redirect('/issue')

    else:
        return render_template('wallet.html', tokens=tokens, notif=notif)

@app.route('/issue', methods=['POST', 'GET'])
def issue():
    global notif
    if request.method == 'POST':
        data = request.form
        infos = data.getlist('info')

        creds = [{
            'user': user,
            'dtype': dtype,
            'info': info
        } for dtype, info in zip(notif['new'], infos)]

        if creds:
            print(f'7. {user} inputs {notif["new"]} info for {notif["fsp"]}')
            print()

            path = host + f'/{notif["fsp"]}/issue'
            requests.post(path, json={'creds': creds})

        return redirect('/')

    else:
        return render_template('issue.html', notif=notif)

@app.route('/store', methods=['POST'])
def store():
    print(f'11. {user} receives and stores tokens')
    print()

    data = request.get_json()

    global tokens
    tokens += data['tokens']

    print('Tokens Stored')
    dfprint(tokens)
    print()

    return ''

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)