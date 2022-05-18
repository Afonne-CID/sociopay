import mimetypes
from . import db


class User(db.Model):
    '''User table
    '''
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    platform = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    signup_date = db.Column(db.DateTime)
    address = db.Column(db.String(250))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(50))
    country = db.Column(db.String(50))
    authenticated = db.Column(db.Boolean, default=False, nullable=False)
    active = db.Column(db.Boolean, default=True)
    user_photo = db.relationship('UserPhoto', backref='user', lazy=True)
    payment = db.relationship('Payment', backref='user', lazy=True)
    bank_details = db.relationship('BankDetails', backref='user', lazy=True)
    virtual_card = db.relationship('VirtualCard', backref='user', lazy=True)


class UserPhoto(db.Model):
    __tablename__ = 'user_photo'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    photo = db.Column(db.String(250), unique=True, nullable=False)
    mimetype = db.Column(db.String(15), nullable=False)
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Payment(db.Model):
    '''Represents the payment table
    '''
    id = db.Column(db.Integer, primary_key=True, unique=True)
    status = db.Column(db.String(10), nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10))
    payment_id = db.Column(db.String(200), nullable=False)
    payment_date = db.Column(db.DateTime)
    trans_ref = db.Column(db.String(250))
    credoref = db.Column(db.String(250))
    payment_option = db.Column(db.String(50), nullable=False)
    payment_slug = db.Column(db.String(100))
    payment_link = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class BankDetails(db.Model):
    '''bank_details table
    '''
    id = db.Column(db.Integer, primary_key=True, unique=True)
    bank = db.Column(db.String(50))
    acct_num = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class VirtualCard(db.Model):
    '''virtual_cards table
    '''
    id = db.Column(db.Integer, primary_key=True, unique=True)
    card_number = db.Column(db.String(16), unique=True)
    card_type = db.Column(db.String(20))
    cvv = db.Column(db.String(7))
    expiry = db.Column(db.DateTime)
    card_balance = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

