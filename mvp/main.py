from flask import *
import requests
import json
from pprint import pprint

from swagger import *

app = Flask(__name__)

subwallet = {}
register('ssn')

@app.route('/user/<user>', methods=['POST', 'GET'])
def index(user):
    global subwallet
    print(subwallet)

    if user not in subwallet:
        subwallet[user] = []

    if request.method == 'POST':
        data = request.form

        # issuing cred
        if data.get('dtype') and data.get('info'):
            issue(data['dtype'], data['info'], user)

            creds = requests.get(
                admin['alice'] + '/credentials'
            ).json()

            referent = sorted(
                creds['results'],
                key = lambda x: int(x['attrs']['timestamp']),
                reverse=True
            )[0]['referent']
            subwallet[user].append(referent)
        
        # request proof
        # check box to offer cred
        dtypes = data.getlist('token')
        if dtypes:
            present(dtypes)
        
    results = [
        requests.get(
            admin['alice'] + '/credential/' + cred_id
        ).json()
        for cred_id in subwallet[user]
    ]

    dtypes = set([
        cred['cred_def_id'].split(':')[-1]
        for cred in results
    ])
        
    return render_template(
        'index.html', 
        dtypes=dtypes
    )

@app.route('/delete', methods=['POST', 'GET'])
def delete():
    credentials = requests.get(
        admin['alice'] + '/credentials'
    ).json()['results']

    for cred in credentials:
        requests.delete(
            admin['alice'] + '/credential/' + cred['referent']
        )

@app.route('/', methods = ['GET', 'POST'])
def conn():
    if request.method == 'POST':
        data = request.form

        requests.post(
            admin['alice'] + '/connections/receive-invitation',
            data=data['invitation']
        )

        return redirect(
            url_for(
                'index',
                user=data['user']
            )
        )

    else:
        inv = requests.post(
            admin['faber'] + '/connections/create-invitation'
        ).json()
        dumped = json.dumps(
            inv['invitation'],
            indent=4
        )
        print(dumped)

        return render_template(
            'conn.html',
            inv=dumped
        )

app.run(port=8080, debug=True)