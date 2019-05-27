"""
from functools import wraps

import bcrypt as bcrypt
from flask import flash, request, redirect, url_for, Blueprint, render_template, session

from database.db import db
from database.models import User

validate = Blueprint("validate", __name__, template_folder="templates")

if request.args.get('key') and query_apikey(request.args.get('key')):  # == "ABC":
    return view_function(*args, **kwargs)
else:
    abort(401)


@validate.route("/validate")
def do_validate():
    if request.args.get('validationID'):
        User.
        (request.args.get('validationID')):  # == "ABC":
        return view_function(*args, **kwargs)
    else:
        abort(401)
"""
import datetime

from flask import Blueprint, flash, redirect, url_for, current_app
from itsdangerous import URLSafeTimedSerializer

from api.apikey import create_apikey
from database.db import db
from database.models import User

validate = Blueprint("validate", __name__, template_folder="templates")


# remove @... and use this function to send a confirmation email
# @validate.route('/confirm/mail/<email>')
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_VALIDATION_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_VALIDATION_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


@validate.route('/confirm/<token>')
# @login_required
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('main_page.main_index'))
    user = User.query.filter_by(email=email).first_or_404()
    if user.validated:
        flash('Account already confirmed. Please login.', 'info')
    else:
        user.validated = True
        # user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        apikey = create_apikey(user.user_id)
        flash('You have confirmed your account. Thanks!', 'success')
        flash('Your API-Key is: {}'.format(apikey), 'info')
    return redirect(url_for('main_page.main_index'))
