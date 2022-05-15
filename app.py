from flask import Flask, request, Response
from flask_sqlachemy import SQLAlchemy
from db import db_init, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:pass@localhost/db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)
db_init(app)



export FLASK_APP=app.py
flask app --host=0.0.0.0 --port=5000