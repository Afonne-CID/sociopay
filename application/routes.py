import uuid
from os import environ as env
from flask import request, make_response
from dotenv import load_dotenv
from datetime import datetime as dt
from flask import current_app as app
from .models import db, User, Payment
from credo.payment import Payment as credo_payment

load_dotenv()

credo_public_key = env['CREDO_PUBLIC_KEY']
credo_secret_key = env['CREDO_SECRET_KEY']
flutter_public_key = env['FLUTTER_PUBLIC_KEY']
flutter_secret_key = env['FLUTTER_PUBLIC_KEY']

payment = credo_payment(credo_public_key, credo_secret_key)

@app.route('/add-user', methods=['POST'])
def add_user():
    new_user = User(
        username = '',
        first_name = '',
        last_name = '',
        email = '',
        platform = '',
        phone = '',
        active = True
    )
    db.session.add(new_user)
    db.session.commit()
    return 'success'

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = db.session.query(User).filter(User.id==id).first()
    res = {}
    res['name'] = '{} {}'.format(user.first_name, user.last_name)
    res['email'] = user.email
    res['phone'] = user.phone
    return res


@app.route('/payment/<user_id>', methods=['GET'])
def get_payment(user_id):
    '''Return all payments that belong to a user
    '''
    user_payment = db.session.query(Payment).join(User, Payment.user_id==user_id).all()
    return user_payment[0].currency


def trans_ref():
    '''Generates unique transref
    '''
    transref = str(uuid.uuid4())
    return str(transref.split('-')[-1])

@app.route('/make-payment', methods=['POST'])
def make_payment():
    val = request.get_json(force=True)
    res = get_user(1)
    status, new_payment = payment.initiate_payment(
        amount=float(val['amount']),
        currency=val['currency'],
        customer_name=res['name'],
        customer_email=res['email'],
        customer_phone=res['phone'],
        trans_ref = trans_ref(),
        payment_options='CARD,BANK',
        redirect_url=''
    )

    if status == 200:
        payment_link = new_payment['paymentLink']
        payment_slug = new_payment['paymentSlug']
        return 'success'
    
# status, verify_payment = payment.verify_payment(transaction_reference=transref)
