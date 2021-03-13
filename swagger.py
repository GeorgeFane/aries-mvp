import requests
import json
from pprint import pprint
import time

# admin API routes
admin = {
    'faber': 'http://0.0.0.0:8021',
    'alice': 'http://0.0.0.0:8031'
}

# get Faber DID
issuer_did = requests.get(
    admin['faber'] + '/wallet/did/public'
).json()['result']['did']

# get list of ids of cred defs that Faber made
# should be 2 things: default education cred from Aries and ssn
definitions = requests.get(
    admin['faber'] + '/credential-definitions/created'
).json()['credential_definition_ids']

# dumb way to get cred names
# ids look like HcnMNFeUxjX1AzpDuP7ZzD:3:CL:52015:ssn
# so split by colon and get last thing
keys = [
    s.split(':')[-1] for s in definitions
]

# easy access cred def ids
# e.g. 'ssn': 'HcnMNFeUxjX1AzpDuP7ZzD:3:CL:52015:ssn'
pairs = dict(
    zip(
        keys, definitions
    )
)

def register(dtype):
    # avoid registering same def twice
    if dtype in keys:
        return

    # create schema
    schema_body = {
        "schema_name": dtype,
        "schema_version": '1.1.1',
        "attributes": [dtype, 'issuer', 'holder', 'timestamp'],
    }    
    schema_response = requests.post(
        admin['faber'] + "/schemas", 
        json=schema_body
    ).json()

    # send to ledger (actually activate)
    schema_id = schema_response["schema_id"]
    credential_definition_body = {
        "schema_id": schema_id,
        "tag": dtype
    }
    cred_def_response = requests.post(
        admin['faber'] + "/credential-definitions", 
        json=credential_definition_body
    ).json()

    # returned vals not stored, but Aries sample does this
    cred_def_id = cred_def_response["credential_definition_id"]   
    return schema_id, cred_def_id

def issue(dtype, info, holder):
    cred_def_id = pairs[dtype]

    # gets Faber's connection id to Alice
    # should by 0th id (most recent)
    connection_id = requests.get(
        admin['faber'] + '/connections'
    ).json()['results'][0]['connection_id']

    # set attrs to pass
    cred_attrs = {
        "holder": holder,
        "issuer": issuer_did,
        dtype: info,
        'timestamp': str(int(time.time()))
    }

    # for each key: value pair, becomes 
    # 'name': key, 'value': value
    cred_preview = {
        "@type": "https://didcomm.org/issue-credential/2.0/credential-preview",
        "attributes": [
            {"name": n, "value": v}
            for (n, v) in cred_attrs.items()
        ],
    }
    
    # final package, contains everything we built
    offer_request = {
        "connection_id": connection_id,
        "comment": f"Offer on cred def id {cred_def_id}",
        "auto_remove": False,
        "credential_preview": cred_preview,
        "filter": {"indy": {"cred_def_id": cred_def_id}},
        "trace": False,
    }

    # returned value not used
    # should check if this contains cred id, to store in user's subwallet
    return requests.post(
        admin['faber'] + "/issue-credential-2.0/send-offer", 
        json=offer_request
    ).json()

def present(dtypes: list):
    req_attrs = [{'name': dtype} for dtype in dtypes]

    # gets Faber's connection id to Alice
    # should by 0th id (most recent)
    connection_id = requests.get(
        admin['faber'] + '/connections'
    ).json()['results'][0]['connection_id']

    # converts 'ssn', 'address' to '0_ssn_uuid', '0_address_uuid'
    # weird, but cred attrs are stored that way in the metadata
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