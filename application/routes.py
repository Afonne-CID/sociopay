import uuid
import json
import requests
from os import environ as env
from flask import request
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
    except Exception as e:
        return f'{e}'

    db.session.add(new_user)
    db.session.commit()

    return {
        'status': 'success',
        'message': 'Registration Successful'
    }

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    
    try:
        return db.session.query(User).filter(User.id==id).first()

    except Exception as e:
        return f'{e}'


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

def diff(first, second):
    '''Returns the difference between two lists'''
    return list(set(first) - set(second)) + list(set(second) - set(first))

@app.route('/make-payment/<user_id>', methods=['POST'])
def make_payment(user_id):

    user = get_user(user_id)

    if type(user) == User:

        transref = trans_ref()
        user_input = request.get_json(force=True)
        platforms = user_input.keys()
        payment_status = {}

        for platform in platforms:
            val = user_input[platform]
            status, new_payment = payment.initiate_payment(
                customer_name=user.first_name + ' ' + user.last_name,
                customer_email=user.email,
                customer_phone=user.phone,
                amount=float(val['amount']),
                currency=val['currency'],
                trans_ref = transref,
                payment_options='CARD,BANK',
                redirect_url=''
            )

            if status == 200:
                payment_link = new_payment['paymentLink']
                payment_slug = new_payment['paymentSlug']

                # Preparing to send payment request
                # headers = {
                #     "Content-Type": "application/json; charset=utf-8",
                #     "Authorization": credo_secret_key
                # }
        
                # data = {
                #     "cardNumber": val["card_number"],
                #     "cardExpiry": val["card_expiry"],
                #     "cvv": val["cvv"]
                # }

                receivers = val['receivers']

                try:
                    #response = requests.post(payment_link, json=data, headers=headers) #Sending the request
                    prepare_pay = Payment(
                            status = 'success', #response['status'],
                            sender = user.username,
                            amount = val['amount'],
                            currency = val['currency'],
                            payment_id = val['payment_id'],
                            payment_date = dt.now(),
                            trans_ref = transref,
                            payment_option = val['payment_option'],
                            credoref = "", #To be supplied from credo
                            payment_slug = payment_slug,
                            payment_link = payment_link,
                            user_id = user_id
                    )

                    users_on_platform = db.session.query(User).filter(User.platform==platform).all()

                    print(users_on_platform)

                    success = []
                    for i in users_on_platform:
                        i.wallet_balance += val['amount']
                        success.append(i.username)
                    
                    
                    db.session.add(prepare_pay)
                    db.session.commit()

                except Exception as e:
                    return f'{e}'

            if len(success) == len(receivers):
                payment_status[platform] = {
                    'status': 'success',
                    'message': 'all payments successful',
                    'receivers': receivers
                }
            else:
                difference = diff(success, receivers)

                for _ in difference:
                    user.wallet_balance += val['amount'] 

                payment_status[platform] = {
                    'status': '{} failed payments were reversed to your account'.format(len(difference)),
                    'message': '{}-> not valid SocioPay registered {} user handles'.format(difference, platform),
                    'receivers': success,
                    'failed': difference
                }
    else:
        return user
    return payment_status

@app.route('/virtual-card/<user_id>', methods=['POST', 'GET'])      
def virutal_card(user_id):
    '''Get and create virtual cards for the given user_id
    '''
    if request.method == 'GET':
        '''Returns card details
        '''
        try:
            virtual_card = db.session.query(VirtualCard).filter(VirtualCard.user_id==user_id).first()
            v = virtual_card
            res = {
                "card_number": v.card_number,
                "card_type": v.card_type,
                "cvv": v.cvv,
                "expiry": v.expiry,
                "card_balance": v.card_balance
            }
            return res
        except:
            return 'No cards found'


    if request.method == 'POST':
        '''Create virtual card for user
        '''
        url = 'https://api.flutterwave.com/v3/virtual-cards'
        val = request.get_json(force=True)
        res = get_user(user_id)

        payload = (
            {  
                'billing_name': res['name'],
                'billing_address': res['address'],
                'billing_city': res['city'],
                'billing_state': res['state'],
                'billing_postal_code': int(res['postal_code']),
                'billing_country': res['country'],
                'currency': val['card_currency'],
                'amount': val['amount'],
                'debit_currency': val['debit_currency']
            }
        )

        headers = { 
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + flutter_secret_key
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return f'{response.text}'
    # status, verify_payment = payment.verify_payment(transaction_reference=transref)
