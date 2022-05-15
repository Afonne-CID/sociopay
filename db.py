from flask_sqlachemy import SQLAlchemy


db = SQLAlchemy()

def db_init(app):
    '''Initiaties the database and creates the tables
    '''
    db.init_app(app)

    with app.app_context():
        '''Creates the database tables
        '''
        db.create_all()