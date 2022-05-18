import uuid
import requests
from os import environ as env
from flask import request, make_response
from dotenv import load_dotenv
from datetime import datetime as dt
from flask import current_app as app
from .models import VirtualCard, db, User, Payment
from credo.payment import Payment as credo_payment

load_dotenv()

credo_public_key = env['CREDO_PUBLIC_KEY']
credo_secret_key = env['CREDO_SECRET_KEY']
flutter_public_key = env['FLUTTER_PUBLIC_KEY']
flutter_secret_key = env['FLUTTER_PUBLIC_KEY']

payment = credo_payment(credo_public_key, credo_secret_key)

@app.route('/add-user', methods=['POST'])
def add_user():
    try:
        user_input = request.get_json(force=True)
        u = user_input
        new_user = User(
            username = u['username'],
            first_name = u['first_name'],
            last_name = u['last_name'],
            email = u['email'],
            platform = u['platform'],
            phone = u['phone'],
            active = True,
            address = u['address'],
            city = u['city'],
            state = u['state'],
            postal_code = u['postal_code'],
            country = u['country'],
            authenticated = False
        )
    except:
        return 'All fields are required'

    db.session.add(new_user)
    db.session.commit()

    return 'success'

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    
    try:
        user = db.session.query(User).filter(User.id==id).first()
        res = {}
        res['name'] = '{} {}'.format(user.first_name, user.last_name)
        res['email'] = user.email
        res['phone'] = user.phone
        res['address'] = user.address
        res['city'] = user.city
        res['state'] = user.state
        res['postal_code'] = user.postal_code
        res['country'] = user.country

        return 'Registration successful'

    except:
        return 'Failed'


@app.route('/payment/<user_id>/<payment_id>', methods=['GET', 'POST'])
def get_payment(user_id, payment_id):
    '''Return all payments that belong to a user
    '''
    payment = db.session.query(Payment).filter(
        Payment.user_id==user_id,
        Payment.payment_id==payment_id
    )
    return f'{payment}'

@app.route('/payments/<user_id>')
def get_payments(user_id):
    '''Return all payments of the `user_id`
    '''
    payments = db.session.query(Payment).filter(
        Payment.user_id==user_id
    )
    return f'{payments}'

def trans_ref():
    '''Generates unique transref
    '''
    trans_ref = str(uuid.uuid4())
    trans_ref = str(trans_ref.split('-')[-1])
    status = db.session.query(Payment).filter(trans_ref==Payment.trans_ref).first()
    while (status):
        trans_ref = str(uuid.uuid4())
        trans_ref = str(trans_ref.split('-')[-1])
        status = db.session.query(Payment).filter(trans_ref==Payment.trans_ref).first()
    return trans_ref


@app.route('/make-payment/<id>', methods=['POST'])
def make_payment(id):
    res = get_user(id)
    trans_ref = trans_ref(),
    user_input = request.get_json(force=True)

    platforms = user_input.keys()
    for platform in platforms:
        val = user_input[platform]
        status, new_payment = payment.initiate_payment(
            amount=float(val['amount']),
            currency=val['currency'],
            customer_name=res['name'],
            customer_email=res['email'],
            customer_phone=res['phone'],
            trans_ref = trans_ref,
            payment_options='CARD,BANK',
            redirect_url=''
        )

        if status == 200:
            payment_link = new_payment['paymentLink']
            payment_slug = new_payment['paymentSlug']

            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": credo_secret_key
            }
    
            data = {
                "cardNumber": val["card_number"],
                "cardExpiry": val["card_expiry"],
                "cvv": val["cvv"]
            }

            receivers = val['receivers']
    
            try:
                response = requests.post(payment_link, json=data, headers=headers)
                prepare_pay = Payment(
                        status = response['status'],
                        sender = val['sender'],
                        amount = val['amount'],
                        currency = val['currency'],
                        payment_id = val['payment_id'],
                        payment_date = dt.now(),
                        trans_ref = trans_ref,
                        payment_option = val['payment_option'],
                        credoref = "",
                        payment_slug = payment_slug,
                        payment_link = payment_link,
                        user_id = id
                    )

                for receiver in receivers:
                    '''Alter receivers' balances
                    '''
                    new_balance = db.session.query(User).filter(
                        User.platform==platform,
                        User.username==receiver
                    ).first()

                    new_balance.balance = val['amount']

                db.session.add(prepare_pay)
                db.session.commit()

            except:
                return {'status': 'failed'}

@app.route('/virtual-card/<id>', methods=['POST', 'GET'])      
def virutal_card(id):
    '''In order for users to request card,
      they'll need to update their profile
    '''
    if request.method == 'GET':
        '''Returns card details
        '''
        virtual_card = db.session.query(VirtualCard).filter(VirtualCard.user_id==id).first()
        v = virtual_card
        res = {
            "card_number": v.card_number,
            "card_type": v.card_type,
            "cvv": v.cvv,
            "expiry": v.expiry,
            "card_balance": v.card_balance
        }
        return res


    if request.method == 'POST':
        '''Create virtual card for user
        '''
        url = 'https://api.flutterwave.com/v3/virtual-cards'
        val = request.get_json(force=True)
        res = get_user(id)

        data = {
            "billing_name": res['name'],
            "billing_address": res['address'],
            "billing_city": res['city'],
            "billing_state": res['state'],
            "billing_postal_code": res['postal_code'],
            "billing_country": res['country'],
            "currency": val['card_currency'],
            "amount": val['amount'],
            "debit_currency": val['debit_currency']
        }

        headers = { 
            "Content-Type": "application/json", 
            "Authorization": flutter_secret_key
        }
        
        response = requests.post(url, data=data, headers=headers)
        return f'{response}'
    # status, verify_payment = payment.verify_payment(transaction_reference=transref)
