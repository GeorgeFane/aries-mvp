from flask import *
import requests
import json
from pprint import pprint

from swagger import *

app = Flask(__name__)

# stores cred ids for each user
# faux multi-wallet system
subwallet = {}

# creates new cred format named ssn
# with attrs: ssn, issuer, holder, timestamp
register('ssn')

# for presenting creds and getting the FSP to issue you creds
@app.route('/user/<user>', methods=['POST', 'GET'])
def index(user):
    global subwallet
    print(subwallet)

    # creates storage for user if nonexistent yet
    if user not in subwallet:
        subwallet[user] = []

    if request.method == 'POST':
        data = request.form

        # issuing cred
        if data.get('dtype') and data.get('info'):
            issue(data['dtype'], data['info'], user)

            # get all credentials across users (not good)
            creds = requests.get(
                admin['alice'] + '/credentials'
            ).json()

            # sort by timestamp, most recent first
            sortedCreds = sorted(
                creds['results'],
                key = lambda x: int(x['attrs']['timestamp']),
                reverse=True
            )

            # get id of most recent cred
            referent = sortedCreds[0]['referent']

            # store id as one of user's
            subwallet[user].append(referent)
        
        # request proof
        # check box to offer cred

        # gets all selected cred types
        dtypes = data.getlist('token')
        if dtypes:
            present(dtypes)
    
    # gets creds by id one-by-one
    # looks at the user's stored ids
    results = [
        requests.get(
            admin['alice'] + '/credential/' + cred_id
        ).json()
        for cred_id in subwallet[user]
    ]

    # set() function to avoid repeats
    # 'cred_def_id' is something long like HcnMNFeUxjX1AzpDuP7ZzD:3:CL:52015:ssn
    # so split by colon to get 'ssn' (cred name) at the end
    dtypes = set([
        cred['cred_def_id'].split(':')[-1]
        for cred in results
    ])

    # pass dtypes (creds that user already has)
    # to show up in user's cred list  
    return render_template(
        'index.html', 
        dtypes=dtypes
    )

# gets ids of all creds across users and deletes by id one-by-one
@app.route('/delete', methods=['POST', 'GET'])
def delete():
    # get all creds
    credentials = requests.get(
        admin['alice'] + '/credentials'
    ).json()['results']

    # delete by id aka referent
    for cred in credentials:
        requests.delete(
            admin['alice'] + '/credential/' + cred['referent']
        )

# for forming connections between agents
@app.route('/', methods = ['GET', 'POST'])
def conn():
    if request.method == 'POST':
        data = request.form

        # Alice agent stores invitation cred in wallet,
        # activates it, and sends corresponding invitation to Faber
        requests.post(
            admin['alice'] + '/connections/receive-invitation',
            data=data['invitation']
        )

        # redirect to user page of whatever name user submitted
        # no actual secure login system yet
        return redirect(
            url_for(
                'index',
                user=data['user']
            )
        )

    else:
        # Faber creates invitation json
        inv = requests.post(
            admin['faber'] + '/connections/create-invitation'
        ).json()

        # formatting
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