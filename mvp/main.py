from flask import *
import requests
import json

from swagger import *

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        data = request.form

        if data.get('dtype') and data.get('info'):
            issue(data['dtype'], data['info'])
        
        dtypes = data.getlist('token')
        print(dtypes)
        if dtypes:
            present(dtypes)
        
    results = requests.get(
        urls['alice'] + '/credentials'
    ).json()['results']

    dtypes = set([
        cred['cred_def_id'].split('.')[-1]
        for cred in results
    ])
        
    return render_template(
        'index.html', 
        dtypes=dtypes
    )

@app.route('/delete', methods=['POST', 'GET'])
def delete():
    credentials = requests.get(
        urls['alice'] + '/credentials'
    ).json()['results']

    for cred in credentials:
        requests.delete(
            urls['alice'] + '/credential/' + cred['referent']
        )

app.run(port=8080, debug=True)