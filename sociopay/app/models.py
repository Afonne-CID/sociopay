import mimetypes
from . import db
from flask_login import UserMixin
from app import db, login_manager
from app.auth.util import hash_pass


class User(db.Model, UserMixin):
    '''User table
    '''
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    platform = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    address = db.Column(db.String(250))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(50))
    country = db.Column(db.String(50))
    password = db.Column(db.LargeBinary)
    authenticated = db.Column(db.Boolean, default=False, nullable=False)
    active = db.Column(db.Boolean, default=True)
    wallet_balance = db.Column(db.Integer, default=0)
    currency = db.Column(db.String(10))
    user_photo = db.relationship('UserPhoto', backref='user', lazy=True)
    payment = db.relationship('Payment', backref='user', lazy=True)
    bank_details = db.relationship('BankDetails', backref='user', lazy=True)
    virtual_card = db.relationship('VirtualCard', backref='user', lazy=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None

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
    receiver = db.Column(db.String(50), nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10))
    payment_reference = db.Column(db.String(200), nullable=False)
    payment_date = db.Column(db.DateTime)
    trans_ref = db.Column(db.String(250))
    credo_ref = db.Column(db.String(250))
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

