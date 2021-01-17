from flask import *
import requests
import json
from pandas import DataFrame

def dfprint(obj):
    df = DataFrame(obj)
    print(df)

fsp = Blueprint('fsp', __name__)
host = 'http://127.0.0.1:8080'
chain = []
db = {}

@fsp.route('/<bank>/create', methods=['POST'])
def create(bank):
    data = request.form
    user = data.get('user')
    dtypes = data.get('dtypestring').split()
    infos = []
    creds = []

    print('1.', user, 'wants to create an account with', bank)
    print('FSP checks chain')
    print()

    global chain
    commits = [
        x for x in chain 
        if x['user'] == user and x['dtype'] in dtypes
    ]
    df = DataFrame(commits)
    
    if commits:
        print('2. Some info submitted previously')
        print('Retrieving corresponding tokens')
        print()

        path = host + '/duo'
        data = {'dtypes': json.dumps(
            list(df.dtype)
        )}
        tokens = json.loads(
            requests.post(path, data=data).content
        )

        print('3. Present tokens to other FSP and retrieve info')
        print()

        infos = [
            json.loads(
                requests.post(
                    f'{host}/{commit["holder"]}/present',
                    data=token
                ).content
            )
            for commit, token in zip(commits, tokens)
        ]

        remaining = list(set(dtypes) - set(df.dtype))
    else:
        print('No priors')
        print()

        remaining = dtypes

    if remaining:        
        print('4. FSP asks for unsubmitted info')
        print()

        path = host + '/prompt'
        data = {'dtypes': json.dumps(remaining)}
        creds = json.loads(
            requests.post(path, data=data).content
        )

        global db
        print('5. Store new submits in FSP\'s individual DB')
        print()
        if not db.get(bank):
            db[bank] = []
        db[bank] += creds        

        chain += [{
            'holder': bank,
            'user': user,
            'dtype': x['dtype']
        } for x in creds]

        print('6. FSP publishes new info dtypes to chain')
        dfprint(chain)
        print()
        
        print('7. FSP gives tokens for newly submitted info')
        print()

        path = host + '/store'
        accessCreds = [{
            'user': user,
            'dtype': dtype
        } for dtype in remaining]

        data = {'tokens': json.dumps(accessCreds)}
        requests.post(path, data=data)
    else:
        print('All info covered by tokens')
        print()

    print(f'Collected info for {bank} account creation')
    dfprint(infos + creds)
    print()

    return 'posted'

@fsp.route('/<bank>/present', methods=['POST'])
def present(bank):
    print('3. Present tokens to other FSP and retrieve info')
    print()

    data = request.form
    user = data['user']
    dtype = data['dtype']

    table = db[bank]
    for x in table:
        if x['user'] == user and x['dtype'] == dtype:
            result = {
                'user': user,
                'dtype': dtype,
                'info': x['info']
            }

    return result