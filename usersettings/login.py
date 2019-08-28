from functools import wraps

import bcrypt as bcrypt
from flask import flash, request, redirect, url_for, Blueprint, render_template, session

from database.db import db
from database.models import User

login = Blueprint("login", __name__, template_folder="templates")


def require_admin(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter_by(user_id=user_id).first()
            if user:
                if not user.validated:
                    flash("Account has to be validated first", 'danger')  # TODO Resend Mail?
                    session.pop("user_id", None)
                    return redirect(url_for('login.do_login'))
                # Success!
                if user.is_admin:
                    return function_to_protect(*args, **kwargs)
                else:
                    flash("Your Account is not allowed to perform this request.", 'warning')
                    return redirect(url_for('main_page.home'))
            else:
                flash("Session exists, but user does not exist (anymore)", 'warning')
                return redirect(url_for('login.do_login'))
        else:
            flash("Please log in", 'warning')
            return redirect(url_for('login.do_login'))

    return wrapper


def require_logged_in(function_to_protect):
    """
    Checks if an existing user is logged in before calling the protected functions.
    :param function_to_protect:
    :return:
    """
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter_by(user_id=user_id).first()
            if user:
                if not user.validated:
                    flash("Account has to be validated first", 'danger')  # TODO Resend Mail?
                    session.pop("user_id", None)
                    return redirect(url_for('login.do_login'))
                # Success!
                return function_to_protect(*args, **kwargs)
            else:
                flash("Session exists, but user does not exist (anymore)", 'warning')
                return redirect(url_for('login.do_login'))
        else:
            flash("Please log in", 'warning')
            return redirect(url_for('login.do_login'))

    return wrapper


@login.route("/login", methods=["GET", "POST"])
def do_login():
    """
    Logs an user in if the email and password are correct and informs the user if something is wrong.
    :return:
    """
    if request.method == "POST":
        # You should really validate that these fields
        # are provided, rather than displaying an ugly
        # error message, but for the sake of a simple
        # example we'll just assume they are provided

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if not user or not check_password(password, user.password):
            # user does not exist in our database OR
            # user exists in the database but password is wrong:
            flash("Email or password wrong, please try again.", 'danger')
            return redirect(url_for('login.do_login'))

        if not user.validated:
            flash("Account has to be validated first", 'danger')  # TODO Resend Mail?
            session.pop("user_id", None)
            return redirect(url_for('login.do_login'))

        # Note we don't *return* the response immediately
        session['user_id'] = user.user_id
        response = redirect(url_for("main_page.main_index"))
        # response.set_cookie('YourSessionCookie', user.user_id)
        return response
    else:
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter_by(user_id=user_id).first()  # db.get(user_id)
            if user:
                # User already logged in
                flash("You are already logged in", "info")
                return redirect(url_for("main_page.main_index"))
            else:
                session.pop("user_id", None)
                flash("Session exists, but user does not exist (anymore)", 'warning')
                return redirect(url_for('login.do_login'))
    # user = db.get(session.get('user_id'))
    # return redirect(url_for('login'))  #
    return render_template('login.html')


def check_password(plain_text_password, hashed_password):
    try:
        return bcrypt.checkpw(plain_text_password.encode('utf8'), hashed_password.encode('utf8'))
    except Exception as e:
        print(e)
        return False
