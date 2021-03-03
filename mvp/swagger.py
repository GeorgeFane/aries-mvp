import requests
import json
from pprint import pprint
import time

admin = {
    'faber': 'http://0.0.0.0:8021',
    'alice': 'http://0.0.0.0:8031'
}

issuer_did = requests.get(
    admin['faber'] + '/wallet/did/public'
).json()['result']['did']

definitions = requests.get(
    admin['faber'] + '/credential-definitions/created'
).json()['credential_definition_ids']

keys = [
    s.split(':')[-1] for s in definitions
]
pairs = dict(
    zip(
        keys, definitions
    )
)

def register(dtype):
    if dtype in keys:
        return

    schema_body = {
        "schema_name": dtype,
        "schema_version": '1.1.1',
        "attributes": [dtype, 'issuer', 'holder', 'timestamp'],
    }    
    schema_response = requests.post(
        admin['faber'] + "/schemas", 
        json=schema_body
    ).json()

    schema_id = schema_response["schema_id"]
    credential_definition_body = {
        "schema_id": schema_id,
        "tag": dtype
    }
    cred_def_response = requests.post(
        admin['faber'] + "/credential-definitions", 
        json=credential_definition_body
    ).json()

    cred_def_id = cred_def_response["credential_definition_id"]   
    return schema_id, cred_def_id

def issue(dtype, info, holder):
    cred_def_id = pairs[dtype]
    connection_id = requests.get(
        admin['faber'] + '/connections'
    ).json()['results'][0]['connection_id']

    cred_attrs = {
        "holder": holder,
        "issuer": issuer_did,
        dtype: info,
        'timestamp': str(int(time.time()))
    }

    cred_preview = {
        "@type": "https://didcomm.org/issue-credential/2.0/credential-preview",
        "attributes": [
            {"name": n, "value": v}
            for (n, v) in cred_attrs.items()
        ],
    }
    
    offer_request = {
        "connection_id": connection_id,
        "comment": f"Offer on cred def id {cred_def_id}",
        "auto_remove": False,
        "credential_preview": cred_preview,
        "filter": {"indy": {"cred_def_id": cred_def_id}},
        "trace": False,
    }

    return requests.post(
        admin['faber'] + "/issue-credential-2.0/send-offer", 
        json=offer_request
    ).json()

def present(dtypes: list):
    req_attrs = [{'name': dtype} for dtype in dtypes]
    connection_id = requests.get(
        admin['faber'] + '/connections'
    ).json()['results'][0]['connection_id']

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

    return requests.post(
        admin['faber'] + "/present-proof/send-request", 
        json=proof_request_web_request
    )