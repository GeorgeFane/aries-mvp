import requests
import json
from pprint import pprint
import time

urls = {
    'faber': 'http://0.0.0.0:8021',
    'alice': 'http://0.0.0.0:8031'
}

connection_id = requests.get(
    urls['faber'] + '/connections'
).json()['results'][0]['connection_id']

issuer_did = requests.get(
    urls['faber'] + '/wallet/did/public'
).json()['result']['did']

schema_ids = requests.get(
    urls['faber'] + '/schemas/created'
).json()['schema_ids']

credential_definition_ids = requests.get(
    urls['faber'] + '/credential-definitions/created'
).json()['credential_definition_ids']

headers = [
    s.split('.')[-1] for s in credential_definition_ids
]
pairs = dict(
    zip(
        headers, credential_definition_ids
    )
)
print(pairs)

presentation_exchange_id = '5c69c270-c43d-4aa6-97f5-45e2cdc5a2a2'

def issue(dtype, info):
    cred_def_id = pairs[dtype]

    requests.post(
        urls['faber'] + '/issue-credential/send',
        json={
            'issuer_did': issuer_did,
            'schema_id': f'{issuer_did}:2:{dtype}:1.1.1',
            'cred_def_id': cred_def_id,
            'connection_id': connection_id,
            'credential_proposal': {
                'attributes':  [{
                    "name": dtype,
                    "value": info
                }]
            }
        }
    )

def present(dtypes: list):
    req_attrs = [{'name': dtype} for dtype in dtypes]

    indy_proof_request = {
        "name": "Proof of KYC",
        "version": "1.0",
        "requested_attributes": {
            f"0_{req_attr['name']}_uuid": req_attr for req_attr in req_attrs
        },
        "requested_predicates": {},
    }

    proof_request_web_request = {
        "connection_id": connection_id,
        "proof_request": indy_proof_request,
        "trace": False,
    }

    requests.post(
        urls['faber'] + "/present-proof/send-request", 
        json=proof_request_web_request
    )

    return

    start = urls['alice'] + f'/present-proof/records/{presentation_exchange_id}'
    credentials = requests.get(start + '/credentials').json()

    requested_attributes = []
    for dtype in dtypes:
        for cred in credentials:
            cred_info = cred['cred_info']['attrs'].get(dtype)
            if cred_info:
                requested_attributes.append(
                    {
                        f'0_{dtype}_uuid': {
                            'cred_id': cred['cred_info']['referent'],
                            'cred_info': cred_info,
                            'revealed': True
                        }
                    }
                )
                break
    print('requested_attributes\n', requested_attributes)

    requests.post(
        start + '/send-presentation',
        json={
            'requested_predicates': {},
            'self_attested_attributes': {},
            'requested_attributes': requested_attributes
        }
    )
