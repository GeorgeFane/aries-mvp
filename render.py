from flask import *
import os

app = Flask(__name__)

print('routes: creds input login partners thanks')

text = 'Date of Birth, Address, Social Security Number'.split(', ')

@app.route('/creds')
def creds():
    return render_template('creds.html', dtypes=text)

@app.route('/input')
def input():
    return render_template('input.html', attrs=text)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/partners', methods=['GET', 'POST'])
def partners():
    if request.method == 'POST':
        return request.form

    path = "static//partners"
    dir_list = os.listdir(path)
    partners = [
        x[:x.index('.')]
        for x in dir_list
    ]

    return render_template(
        'partners.html', 
        partners=partners
    )

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

app.run(debug=True, port=8080)