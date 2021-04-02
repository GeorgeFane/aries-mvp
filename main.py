from flask import *
import requests
import json
from pprint import pprint
import time

from swagger import *

app = Flask(__name__)

# creates new cred format named ssn
# with attrs: ssn, issuer, holder, timestamp
attrs = 'ssn address'.split()
for x in attrs:
    register(x)

# thank you page, to tell user they're done
@app.route('/thanks', methods=['POST', 'GET'])
def thanks():
    if request.method == 'POST':
        return redirect(url_for('partners'))

    return render_template(
        'thanks.html'
    )

# for inputting fresh info
@app.route('/index', methods=['POST', 'GET'])
def index():
    # PII that FSP has, from creds
    dtypes = request.args.getlist('dtypes')

    # PII that FSP still doesn't have
    remaining = set(attrs) - set(dtypes)

    if request.method == 'POST' or not remaining:
        data = request.form

        # issuing cred
        for dtype in remaining:
            # check if input is not empty
            if data.get(dtype):
                issue(dtype, data[dtype])

        return redirect(url_for('thanks'))

    # pass dtypes (creds that user already has)
    # to show up in user's cred list  
    return render_template(
        'input.html',
        attrs=remaining
    )

# for presenting creds, before inputting fresh info
@app.route('/creds', methods=['POST', 'GET'])
def creds():    
    # gets all creds
    results = requests.get(
        admin['alice'] + '/credentials'
    ).json()['results']

    if request.method == 'POST' or not results:
        data = request.form
        
        # request proof
        # gets all selected cred types
        dtypes = data.getlist('token')
        if dtypes:
            present(dtypes)

        # pass which creds are presented, so don't ask
        return redirect(url_for('index', dtypes=dtypes))

    # set() function to avoid repeats
    # 'cred_def_id' is something long like HcnMNFeUxjX1:3:CL:52015:Faber.Agent.ssn
    # so split by dot to get 'ssn' (cred name) at the end
    dtypes = set([
        cred['cred_def_id'].split('.')[-1]
        for cred in results
    ])

    # pass dtypes (creds that user already has)
    # to show up in user's cred list  
    return render_template(
        'creds.html', 
        dtypes=dtypes,
        attrs=attrs
    )

# shows held creds and FSP partners
@app.route('/partners', methods=['GET', 'POSt'])
def partners():    
    if request.method == 'POST':
        # the method is POST if the user taps an FSP's icon

        # Faber creates invitation json
        # in final version, user gets an invitation specific to the FSP they tapped
        invitation = requests.post(
            admin['faber'] + '/connections/create-invitation'
        ).json()['invitation']

        # Alice accepts invitation
        connection = requests.post(
            admin['alice'] + '/connections/receive-invitation',
            json=invitation
        ).json()

        print()
        print('CONNECTED WITH FSP')
        pprint(connection)

        return redirect(url_for('creds'))

    print()
    print('IMAGINE CREDS SHOW UP AFTER A COUPLE DAYS (VERIFICATION)')
    print('HOME SCREEN')

    # gets all creds
    results = requests.get(
        admin['alice'] + '/credentials'
    ).json()['results']

    # get format names of held creds
    dtypes = set([
        cred['cred_def_id'].split('.')[-1]
        for cred in results
    ])

    # pass dtypes (creds that user already has)
    # to show up in user's cred list  
    return render_template(
        'partners.html', 
        dtypes=dtypes
    )

@app.route('/', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST':
        return redirect(url_for('partners'))

    print('LOGIN SCREEN')
    return render_template(
        'login.html'
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

    return redirect(url_for('partners'))

app.run(port=8080, debug=True)