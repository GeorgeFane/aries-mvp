from flask import *
import requests
import json
from pandas import DataFrame

def dfprint(obj):
    df = DataFrame(obj)
    print(df)

fsp = Blueprint('fsp', __name__, url_prefix='/<bank>')
host = 'http://127.0.0.1:8080'
chain = []
db = {}
reqs = {
    'paypal': ('ssn', 'dob'),
    'fidelity': ('ssn', 'address'),
    'goldman': ('dob', 'address')
}

@fsp.route('/create', methods=['POST'])
def create(bank):
    global chain
    data = request.get_json()
    user = data['user']
    dtypes = reqs[bank]

    print('1.', user, 'wants to create an account with', bank)
    print('FSP checks chain')
    print()
    commits = [
        x for x in chain 
        if x['user'] == user and x['dtype'] in dtypes
    ]
    df = DataFrame(commits)

    old = []
    if commits:
        old = df.dtype

        print(f'2. {bank} found prior submits for {user}')
        dfprint(old)
        print()

    data = {
        'fsp': bank,
        'old': list(old),
        'new': list(set(dtypes) - set(old))
    }
    requests.post(host + '/duo', json=data)

    return ''
        
@fsp.route('/issue', methods=['POST'])
def issue(bank):
    global chain
    data = request.get_json()
    creds = data['creds']
    
    if not db.get(bank):
        db[bank] = []
    db[bank] += creds

    print(f'8. {bank} stores submitted info in DB')
    dfprint(db[bank])
    print()

    tokens = [{
        'holder': bank,
        'user': cred['user'],
        'dtype': cred['dtype']
    } for cred in creds]
    chain += tokens

    print(f'9. {bank} publishes about new info to chain')
    dfprint(chain)
    print()
    
    print(f'10. {bank} gives tokens for new info')
    print()

    path = host + '/store'
    data = {'tokens': tokens}
    requests.post(path, json=data)

    return ''
        
@fsp.route('/auth', methods=['POST'])
def auth(bank):
    print(f'4. {bank} receives tokens and presents them sequentially to info holders')
    print()

    data = request.get_json()
    for token in data:
        requests.post(f'{host}/{token["holder"]}/present', json={
            'token': token,
            'sender': bank
        })

    return ''
    
@fsp.route('/present', methods=['POST'])
def present(bank):
    data = request.get_json()
    token = data['token']
    sender = data['sender']

    print(f'5. {bank} is presented the {token["dtype"]} token from {token["user"]}')
    print()

    table = db[bank]
    for x in table:
        if x['user'] == token['user'] and x['dtype'] == token['dtype']:
            result = {
                'user': token['user'],
                'dtype': token['dtype'],
                'info': x['info']
            }
            break
    
    path = f'{host}/{sender}/respond'
    requests.post(path, json=result)

    return ''
        
@fsp.route('/respond', methods=['POST'])
def respond(bank):
    data = request.get_json()
    
    if not db.get(bank):
        db[bank] = []
    db[bank].append(data)

    print(f'6. {bank} stores returned info in DB')
    dfprint(db[bank])
    print()

    return ''