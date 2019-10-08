import time

import bcrypt
from flask import Blueprint, render_template, redirect, request, session, flash, url_for

from api.mail import send_mail
from database.db import db
from database.models import User
from usersettings.validate import generate_confirmation_token

signup = Blueprint("signup", __name__, template_folder="templates")


def gen_password(plaintext):
    return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt(12)).decode('utf-8')


@signup.route('/signup', methods=['GET', 'POST'])
def register():
    """
    Registers a new user if the user isn't already logged in and the email isn't used. Also sends an email to the user
    to confirm the email address.
    :return:
    """
    user_logged_in = session.get("user_id")
    if user_logged_in:
        flash("You cant create a new Account. You are already logged in.", "warning")
        return redirect(url_for("main_page.main_index"))

    if request.method == "POST":
        # You should really validate that these fields
        # are provided, rather than displaying an ugly
        # error message, but for the sake of a simple
        # example we'll just assume they are provided

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()  # _or_404()

        if user:
            # Again, throwing an error is not a user-friendly
            # way of handling this, but this is just an example
            flash("Account already exists for this E-Mail", "warning")
            return render_template('signup.html')
        else:
            user = User(email=email, password=gen_password(password),
                        created=int(time.time()),
                        validated=False)
            db.session.add(user)
            db.session.commit()
            # Note we don't *return* the response immediately
            # session['user_id'] = user.user_id
            # response = redirect(url_for("main_page.main_index"))
            # response.set_cookie('YourSessionCookie', user.user_id)
            send_mail(None, [user.email],
                      "Use this link to confirm your E-Mail: " + request.host + "/confirm/" +
                      generate_confirmation_token(user.email))
            flash("Signup complete, please confirm your E-Mail", "info")
            return redirect(url_for("main_page.main_index"))
    else:
        return render_template('signup.html')
