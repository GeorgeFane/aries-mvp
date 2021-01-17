from flask import *
import requests
from fsp import fsp, dfprint
import json
import sys

app = Flask(__name__)
app.register_blueprint(fsp)

host = 'http://127.0.0.1:8080'
did = 'did:example:3c1yq1k3snydmwwx15enif'
tokens = []

@app.route('/')
def index():
    return render_template('user.html')

@app.route('/', methods=['POST'])
def indexpost():
    print('0. START')
    print()

    data = request.form
    bank = data.get('fsp')
    dtypestring = data.get('dtypes')

    path = f'/{bank}/create'
    data = {
        'user': did,
        'dtypestring': dtypestring
    }
    requests.post(host + path, data=data)

    return 'posted'

@app.route('/prompt', methods=['POST'])
def prompt():
    print('4. FSP asks for unsubmitted info')
    print()

    data = request.form
    dtypes = json.loads(
        data.get('dtypes')
    )

    print('Input KYC info for', dtypes)
    infos = [input(dtype + ': ') for dtype in dtypes]
    print()

    creds = [{
        'user': did,
        'dtype': dtype,
        'info': info
    } for dtype, info in zip(dtypes, infos)]
    credstring = json.dumps(creds)

    return credstring

@app.route('/store', methods=['POST'])
def store():
    print('7. FSP gives tokens for newly submitted info')
    print()

    data = request.form

    global tokens
    tokens += json.loads(
        data.get('tokens')
    )

    print('Tokens Stored')
    dfprint(tokens)
    print()

    return 'stored'

@app.route('/duo', methods=['POST'])
def duo():
    print('2. Some info submitted previously')
    print('Retrieving corresponding tokens')
    print()

    data = request.form
    dtypes = json.loads(
        data.get('dtypes')
    )

    print('Approve giving tokens for', dtypes)
    yesnos = [input(dtype + ' [y/n]: ') for dtype in dtypes]

    if all([x == 'y' for x in yesnos]):
        print('All tokens approved')
        print()

        approved = [
            token for token in tokens
            if token['dtype'] in dtypes
        ]

        appstring = json.dumps(approved)
        return appstring
    else:
        print('Guess you don\'t want to create an account then')
        print()
        return ''

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)