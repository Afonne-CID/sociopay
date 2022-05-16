from os import environ as env
from flask import request, make_response
from dotenv import load_dotenv
from datetime import datetime as dt
from flask import current_app as app
from .models import db, User #, Payment

@app.route('/', methods=['POST', 'GET'])
def add_user():
    if request.method == 'GET':
        new_user = User(
            username = 'afonneblog',
            first_name = 'Paul',
            last_name = 'Afonne-CID',
            email = 'cid@afonne.com',
            platform = 'instagram',
            phone = '08071231219',
            signup_date = dt.now(),
            active = 'True'
        )

        db.session.add(new_user)
        db.session.commit()

'''from credo.payment import Payment

load_dotenv()

payment = Payment(env['PUBLIC_KEY'], env['SECRET_KEY'])

def transref_gen():
    Generates unique transref

@app.route('/make-payment', method=['POST'])
def make_payment(val):
    transref = transref_gen()
    {   'platform': 'pname',
        'unames': ['uname1', 'uname2', 'uname3', 'uname4'],
        'amount': 0,
        'currency': 'NGN',
        'card_number': '02xxxxxxxxxxx',
        'card_expiry': str('date'),
        'CVV': '000',
        'successpage': 'llsslsissl.com',
        'sender': 'send_uname'
    }
   
    test_card = 
    Card Number': 5473 5001 6000 1018
    Expiry: 12/25
    CVV: 123
    PIN: 0000
    

    c = User.query.filter(User.username == val['sender'].first())
    c_name, c_email, c_phone = c.first_name + c.last_name, c.email, c.phone

    status, new_payment = payment.initiate_payment(
        amount=float(val['amount']), currency=['currency'], customer_name=c_name,
        customer_email=c_email,
        customer_phone=c_phone,
        payment_options='CARD,BANK',
        redirect_url=''
    )

    {
        "status": "success",
        "message": "Redirect browser to the payment link",
        "paymentLink": "https://credocentral.com/paymentgateway/l986g24r66fs",
        "paymentSlug": "l986g24r66fs"
    }
    payment_link = new_payment['paymentLink']

    status, verify_payment = payment.verify_payment(transaction_reference=transref)
    '''
