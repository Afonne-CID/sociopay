import mimetypes
from db import db


class User(db.Model):
    '''User table
    '''
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    platform = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    signup_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean)

class UserPhoto(db.Model):
    '''Represents user_photo table
    '''
    __tablename__ = 'user_photo'
    id = id.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Text, unique=True, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime)
    user_id = id.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=backref('user', uselist=False))

class Payment(db.Model):
    '''Represents the payment table
    '''
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    receiver = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10))
    payment_id = db.Column(db.String(200), nullable=False)
    payment_date = db.Column(db.DateTime)
    transref = db.Column(db.String(250))
    credoref = db.Column(db.String(250))
    payment_option = db.Column(db.String(50), nullable=False)
    payment_slug = db.Column(db.String(100))
    payment_link = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=backref('user', uselist=False))
