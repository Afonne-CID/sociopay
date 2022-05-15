#!/usr/bin/env python
from os import environ as env
from dotenv import load_dotenv
from credo.banks_and_currencies import BanksCurrencies


load_dotenv()
public_key = env['PUBLIC_KEY']
secret_key = env['SECRET_KEY']

{'platform': {
        unames: ['uname1', 'uname2', 'uname3', 'uname4'],
        amount: 0,
        currency: 'NGN'
        card_number: '02xxxxxxxxxxx',
        card_expiry: str(date),
        CVV: '000',
        successpage: 'llsslsissl.com',
        sender: 'send_uname'
    }
}