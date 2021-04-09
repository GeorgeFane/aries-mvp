from flask import *
import os

app = Flask(__name__)

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

@app.route('/partners')
def partners():
    path = "static//partners"
    dir_list = os.listdir(path)
    return render_template('partners.html', dir_list=dir_list)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

app.run(debug=True, port=8080)