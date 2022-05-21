# -*- encoding: utf-8 -*-
import uuid
import requests
from urllib.parse import urlparse, parse_qs
from os import environ as env
from dotenv import load_dotenv
from app.home import blueprint
from app.home.forms import CreatePayment
from flask_login import current_user
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from ..models import db, User, Payment, UserPhoto
from urllib.parse import urlparse, parse_qs
from credo.payment import Payment as credo_payment


load_dotenv()

credo_public_key = env['CREDO_PUBLIC_KEY']
credo_secret_key = env['CREDO_SECRET_KEY']
flutter_public_key = env['FLUTTER_PUBLIC_KEY']
flutter_secret_key = env['FLUTTER_PUBLIC_KEY']

payment = credo_payment(credo_public_key, credo_secret_key)

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

def overview():
    payments = db.session.query(Payment).filter(Payment.user_id==current_user.id).all()
    total_sent = 0
    total_received = 0
    total_deposit = 0
    for payment in payments:
        if payment.receiver != current_user.username:
            total_sent += payment.amount
    all_payments = db.session.query(Payment).filter(Payment.receiver==current_user.username).all()
    for each_payment in all_payments:
        if payment.sender != current_user.username:
            total_received += each_payment.amount
    for each in all_payments:
        if each.sender == current_user.username:
            total_deposit += each.amount
    return {
        'total_sent': total_sent,
        'total_received': total_received,
        'total_deposit': total_deposit
    }

@blueprint.route('/index')
@login_required
def index():
    
    recent_payments = db.session.query(Payment).filter(Payment.user_id==current_user.id).limit(10)
    res = overview()
    return render_template(
            'home/index.html',
            segment='index',
            payments=recent_payments,
            total_sent=res['total_sent'],
            total_received=res['total_received'],
            total_deposit=res['total_deposit']
        )

@blueprint.route('/sent-transactions')
@login_required
def sent_transactions():
    per_page = 10
    payments = db.session.query(Payment).filter(Payment.user_id==current_user.id).paginate(1,per_page,error_out=False)
    res = overview()
    return render_template(
        'sent-transactions.html',
        payments=payments,
        total_sent=res['total_sent'],
        total_received=res['total_received'],
        total_deposit=res['total_deposit']
    )

@blueprint.route('/received-transactions')
@login_required
def received_transactions():
    per_page = 10
    payments = db.session.query(Payment).filter(Payment.receiver==current_user.username).paginate(1,per_page,error_out=False).all()
    res = overview()
    return render_template(
        'received-transactions.html',
        payments=payments,
        total_sent=res['total_sent'],
        total_received=res['total_received'],
        total_deposit=res['total_deposit']
    )

@blueprint.route('/make-payment', methods=['GET', 'POST'])
@login_required
def make_payment():

    create_payment = CreatePayment(request.form)

    platforms = ['instagram', 'twitter', 'google', 'sociopay']
    payment_option = ['CARD', 'BANK']
    transref = trans_ref()
    user = db.session.query(User).filter(User.id==current_user.id).first()

    if 'start' in request.form:

        input_amount = request.form['amount']

        # payment_status = {}

        try:
            int(input_amount) <= 5
            input_amount = float(input_amount)

            status, new_payment = payment.initiate_payment(
                customer_name=user.first_name + ' ' + user.last_name,
                customer_email=user.email,
                customer_phone=user.phone,
                amount=input_amount,
                currency=current_user.currency,
                trans_ref = transref,
                payment_options='CARD,BANK',
                redirect_url='/payment-status'
            )
            
            if status == 200:
                payment_link = new_payment['paymentLink']
                payment_slug = new_payment['paymentSlug']

                return render_template('home/make-payment.html',
                        payment_link=payment_link,
                        form=create_payment,
                        payment_option=payment_option,
                        platforms=platforms,
                        success=True,
                        user=user
                )

            else:
                return render_template('home/make-payment.html',
                    error=status,
                    success=False,
                    form=create_payment,
                    payment_option=payment_option,
                    platforms=platforms,
                    user=user)
        except:
            return render_template('home/make-payment.html',
                msg="Amount must be valid integer and greater than 5",
                form=create_payment,
                payment_option=payment_option,
                platforms=platforms,
                success=False,
                user=user
        )

    else:

        response = requests.get('home/make-payment.html')
        if response.history:
            parsed_url = urlparse(response.url)
            credoref = parse_qs(parsed_url.query)['credoRef'][0]
            transref = parse_qs(parsed_url.query)['transRef'][0]

            status, verify_payment = payment.verify_payment(transaction_reference=transref)

            if status == 200:
                val = {
                    'transref': transref,
                    'credoref': credoref,
                    
                }

                save_payment(verify_payment, val, user)
                return render_template('home/make-payment.html',
                    success=False,
                    payment_success=True,
                    form=create_payment,
                    receivers=request.form['receivers'],
                    payment_option=payment_option,
                    platforms=platforms,
                    user=user)
            else:
                save_payment(verify_payment, credoref, transref, user)
                return render_template('home/make-payment.html',
                    success=False,
                    payment_success=False,
                    form=create_payment,
                    payment_option=payment_option,
                    platforms=platforms,
                    receivers=request.form['receivers'],
                    user=user)
        else:
            return render_template('home/make-payment.html',
                success=False,
                form=create_payment,
                payment_option=payment_option,
                platforms=platforms,
                user=user)

# @blueprint.route('/payment-status')
# @login_required
# def process_payment():
#     if request.method == 'POST':

def save_payment(verify_payment, transref, credoref, user):
    try:
        prepare_pay = Payment(
                status = verify_payment['paymentStatus']['name'],
                sender = user.username,
                amount = val['amount'],
                currency = val['currency'],
                payment_reference = verify_payment['referenceNo'],
                payment_date = verify_payment['date'],
                trans_ref = transref,
                payment_option = val['payment_option'],
                credoref = credoref, #To be supplied from credo
                payment_slug = payment_slug,
                payment_link = payment_link,
                user_id = user_id
        )

        users_on_platform = db.session.query(User).filter(User.platform==platform).all()

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

    {
    "id": 4,
    "completedAt": "2021-01-28T12:35:43",
    "createdAt": "2021-01-28T12:35:43",
    "customerEmail": "cirochwukunle@example.com",
    "customerName": "Ciroma Chukwuma Adekunle",
    "customerPhoneNo": "2348012345678",
    "customerUuid": null,
    "date": "2021-01-28",
    "description": "Transaction",
    "dueAmount": 100,
    "merchantImsId": "154789685478965",
    "merchantReferenceNo": "254655-4946-3634",
    "processingFees": "1.5,",
    "customerCharge": "0.0,",
    "referenceNo": "order-URQiaJZRvd",
    "totalAmount": 101.5,
    "updatedAt": "2021-01-28T12:35:43",
    "approvalStatus": {
        "id": 2,
        "name": "Accepted"
    },
    "paymentChannel": {
        "id": 1,
        "name": "Card"
    },
    "paymentStatus": {
        "id": 5,
        "description": null,
        "name": "Successful"
    },
    "paymentOption": {
        "id": 1,
        "name": "Regular"
    }
}


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.htm
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
