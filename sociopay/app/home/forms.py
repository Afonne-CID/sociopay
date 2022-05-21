from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField

class CreatePayment(FlaskForm):
    receivers = TextAreaField('Receivers',
                            id='receivers')
    amount = IntegerField('Amount',
                            id='amount')
    platforms = StringField('Social media platforms',
                        id='platforms')