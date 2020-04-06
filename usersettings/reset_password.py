import random
import string
from flask import Blueprint, request, flash, redirect, url_for, session, render_template

from database.db import db
from database.models import User
from api.mail import send_mail
from usersettings.register import gen_password

reset = Blueprint("reset", __name__, template_folder="templates")


def random_string_digits(string_length=6):
    """Generate a random string of letters and digits """
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.SystemRandom().choice(letters_and_digits) for i in range(string_length))


@reset.route('/reset_password', methods=['GET', 'POST'])
def new_reset_password():
    """
    Confirms the user if the confirm_token is valid and the user isn't already confirmed.
    :param token:
    :return:
    """
    if request.method == "GET":
        return render_template('reset_password.html')
    else:
        email = request.form["email"]
        if not email:
            flash('The reset-token is invalid or has expired.', 'danger')
            return redirect(url_for('main_page.main_index'))
        user = User.query.filter_by(email=email).first()
        if user and user.validated:
            send_mail(None, [user.email],
                      "Use this link to reset your Password: " + request.host_url + "/reset_password/" +
                      user.get_password_reset_token() + "\nIf you did not request a Password reset you can ignore this E-Mail",
                      subject="[MESA] Your requested Password-reset")
        flash('If this E-Mail belongs to an activated (!) account it should receive an E-Mail containing a Reset-Link',
              'success')
        return redirect(url_for('main_page.main_index'))


@reset.route('/reset_password/<token>', methods=['GET', 'POST'])
def confirm_reset_password(token):
    """
    Confirms if the confirm_token is valid and - if it is valid - sends an email with a new password.
    :param token:
    :return:
    """
    user = User.verify_password_reset_token(token)
    if user is None:
        flash('This Token is invalid or has expired.', 'danger')
        return redirect(url_for('main_page.main_index'))
    if user.validated:
        new_pass = random_string_digits(16)
        user.password = gen_password(new_pass)
        db.session.add(user)
        db.session.commit()
        send_mail(None, [user.email],
                  "Your new Password: " + new_pass + "\nYou can change it in your profile.",
                  subject="[MESA] Your new Password for MESA DNA Simulator")
        flash('A new password hat been generated and will be sent to you by mail', 'success')
        session['user_id'] = user.user_id
    else:
        flash('Account not activated yet!', 'warning')
    return redirect(url_for('main_page.main_index'))
