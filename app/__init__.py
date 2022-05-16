from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def create_app():
    '''Construct the core application'''
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app) # Initiaties the database

    with app.app_context():
        '''Creates the database tables
        '''
        db.create_all()
    return app