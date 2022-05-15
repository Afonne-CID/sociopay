from os import environ as env
from dotenv import load_dotenv
from flask import Flask, request, Response
from flask_sqlachemy import SQLAlchemy
from db import db_init, db

load_dotenv()
user = env['USER']
pwd = env['PWD']
db = env['DB']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+user+':'+pwd+'@localhost/'+db
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)
db_init(app)

@app.route('/make-payment', method=['POST'])
def make_payment(dict_val):
    '''Makes payment'''

export FLASK_APP=app.py
flask app --host=0.0.0.0 --port=5000