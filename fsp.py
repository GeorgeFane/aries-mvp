from flask import *
import requests
import json
from pandas import DataFrame
from google.cloud import datastore
import os

path = 'contract/datastore-creds.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
client = datastore.Client()

def dfprint(obj):
    df = DataFrame(obj)
    print(df)

def put(creds: list, kind: str):
    ents = []
    for cred in creds:
        key = client.key(kind)
        ent = datastore.Entity(key)
        ent.update(cred)
        ents.append(ent)
    client.put_multi(ents)

fsp = Blueprint('fsp', __name__, url_prefix='/<bank>')
host = 'http://127.0.0.1:8080'
reqs = {
    'paypal': ('ssn', 'dob'),
    'fidelity': ('ssn', 'address'),
    'goldman': ('dob', 'address')
}

@fsp.route('/create', methods=['POST'])
def create(bank):
    data = request.get_json()
    user = data['user']
    dtypes = reqs[bank]

    print('1.', user, 'wants to create an account with', bank)
    print('FSP checks chain')
    print()

    query = client.query(kind='chain')
    query.add_filter('user', '=', user)
    commits = [
        result for result in list(query.fetch()) 
        if result['dtype'] in dtypes
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
    data = request.get_json()
    creds = data['creds']

    put(creds, bank)
    query = client.query(kind=bank)
    results = list(query.fetch())

    print(f'8. {bank} stores submitted info in DB')
    dfprint(results)
    print()

    tokens = [{
        'holder': bank,
        'user': cred['user'],
        'dtype': cred['dtype']
    } for cred in creds]
    put(tokens, 'chain')

    query = client.query(kind='chain')
    chain = list(query.fetch())

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

    query = client.query(kind=bank)
    query.add_filter('user', '=', token['user'])
    query.add_filter('dtype', '=', token['dtype'])
    result = list(query.fetch())[0]
    
    path = f'{host}/{sender}/respond'
    requests.post(path, json=result)

    return ''
        
@fsp.route('/respond', methods=['POST'])
def respond(bank):
    data = request.get_json()

    put([data], bank)

    query = client.query(kind=bank)
    results = list(query.fetch())

    print(f'6. {bank} stores returned info in DB')
    dfprint(results)
    print()

    return ''