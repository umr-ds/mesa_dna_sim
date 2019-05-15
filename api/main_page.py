from flask import Blueprint, render_template, redirect, session, request, flash, url_for

from api.RateLimit import ratelimit, get_view_rate_limit
from api.apikey import require_apikey
from database.db import db
from database.models import User, Apikey
from usersettings.login import require_logged_in, check_password
from usersettings.register import gen_password

main_page = Blueprint("main_page", __name__, template_folder="templates")


#
# Since Flask will only be used for the API we will redirect to the main page
#
@main_page.route("/")
def main_index():
    return render_template('index.html')
    # return redirect("http://dnasimulator.mosla.de", code=302)


@main_page.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response


@main_page.route("/api", methods=["GET"])
def home():
    return render_template("index.html"), 200


@main_page.route('/profile', methods=["GET", "POST"])
# @require_apikey
# @ratelimit(limit=300, per=60 * 15)
@require_logged_in
def profile():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    if request.method == "POST":
        if "new_email" in request.form:
            new_email = request.form["new_email"]
            # we got a change email update
            user.email = new_email
            db.session.add(user)
            db.session.commit()
        else:
            # we got a change password update
            old_password = request.form["old_password"]

            new_password = request.form["new_password"]
            new_password2 = request.form["new_password2"]

            if not user or not check_password(old_password, user.password):
                flash("Could not set new Password. Did you enter the correct password?", "warning")
                return render_template('profile.html')
            else:
                if new_password == new_password2:
                    user.password = gen_password(new_password)
                    db.session.add(user)
                    db.session.commit()
                    flash("Password updated!", "success")
                else:
                    flash("Passwords do not match.", "warning")
                    return render_template('profile.html')
    if user_id and user:
        keys = Apikey.query.filter_by(owner_id=user_id).all()
        return render_template('profile.html', apikeys=keys, current_email=user.email)
    return render_template('profile.html')


@main_page.route('/rate-limited')
@require_apikey
@ratelimit(limit=300, per=60 * 15)
def index():
    return '<h1>This is a rate limited response</h1>'


@main_page.route("/query_sequence", methods=['GET', 'POST'])
@require_logged_in
def query_sequence():
    user_id = session.get('user_id')
    # user = User.query.filter_by(user_id=user_id).first()
    apikey_obj = Apikey.query.filter_by(owner_id=user_id).first()
    if request.method == "POST":
        sequence = request.json.get('sequence')
        return render_template('sequence_view.html', apikey=apikey_obj.apikey)
    else:
        sequence = request.args.get('sequence')
        return render_template('sequence_view.html', apikey=apikey_obj.apikey, sequence=sequence)
