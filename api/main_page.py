import re

from flask import Blueprint, render_template, redirect, session, request, flash, url_for, jsonify
from sqlalchemy import desc

from api.RateLimit import ratelimit, get_view_rate_limit
from api.apikey import require_apikey
from database.db import db
from database.models import User, Apikey, UndesiredSubsequences
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
    apikey_obj = Apikey.query.filter_by(owner_id=user_id).first()
    if request.method == "POST":
        sequence = request.json.get('sequence')
        return render_template('sequence_view.html', apikey=apikey_obj.apikey)
    else:
        sequence = request.args.get('sequence')
        return render_template('sequence_view.html', apikey=apikey_obj.apikey, sequence=sequence, host=request.host)


@main_page.route("/undesired_subsequences", methods=['GET', 'POST'])
@require_logged_in
def undesired_subsequences():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    if user_id and user:
        if request.method == "POST":
            # TODO

            print("TODO, update sequences")
        undesired_sub_seq = UndesiredSubsequences.query.filter_by(owner_id=user_id).order_by(
            desc(UndesiredSubsequences.id)).all()
        return render_template('undesired_subsequences.html', usubsequence=undesired_sub_seq, host=request.host)
    else:
        flash("Could not find user, please login again", 'warning')
        session.pop('user_id')
        return render_template("index.html"), 200


@main_page.route("/api/delete_subsequence", methods=['POST'])
@require_logged_in
def delete_subsequences():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    sequence_id = request.form.get('sequence_id')
    if user_id and user and sequence_id is not None:
        undesired_sub_seq = UndesiredSubsequences.query.filter_by(owner_id=user_id, id=sequence_id).first()
        db.session.delete(undesired_sub_seq)
        db.session.commit()
        return jsonify({'did_succeed': True, 'deleted_id': sequence_id})
    else:
        return jsonify({'did_succeed': False, 'deleted_id': sequence_id})


@main_page.route("/api/add_subsequence", methods=['POST'])
@require_logged_in
def add_subsequences():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    sequence = sanitizeInput(request.form.get('sequence'))
    error_prob = request.form.get('error_prob')
    if user_id and user and sequence is not None and sequence != "" and error_prob is not None:
        try:
            error_prob = float(error_prob)
            new_subsequence = UndesiredSubsequences(sequence=sequence, error_prob=error_prob, validated=False,
                                                    owner_id=user_id)
            db.session.add(new_subsequence)
            db.session.commit()
            return jsonify(
                {'did_succeed': True, 'sequence': new_subsequence.sequence, 'error_prob': new_subsequence.error_prob,
                 'id': new_subsequence.id, 'created': new_subsequence.created, 'validated': new_subsequence.validated})
        except:
            return jsonify({'did_succeed': False})
    else:
        return jsonify({'did_succeed': False})


@main_page.route("/api/update_subsequence", methods=['POST'])
@require_logged_in
def update_subsequences():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    sequence_id = request.form.get('sequence_id')
    sequence = sanitizeInput(request.form.get('sequence'))
    error_prob = request.form.get('error_prob')
    if user_id and user and sequence_id is not None and sequence is not None and sequence != "" and error_prob is not None:
        try:
            error_prob = float(error_prob)
            curr_sub_seq = UndesiredSubsequences.query.filter_by(owner_id=user_id, id=sequence_id).first()
            curr_sub_seq.error_prob = error_prob
            curr_sub_seq.sequence = sequence
            curr_sub_seq.validated = False

            # db.session.add(curr_sub_seq)
            db.session.commit()
            return jsonify(
                {'did_succeed': True, 'sequence': curr_sub_seq.sequence, 'error_prob': curr_sub_seq.error_prob,
                 'id': curr_sub_seq.id, 'created': curr_sub_seq.created, 'validated': curr_sub_seq.validated})
        except:
            return jsonify({'did_succeed': False})
    else:
        return jsonify({'did_succeed': False})


def sanitizeInput(input, regex=r'[^a-zA-Z]'):
    result = re.sub(regex, "", input)
    return result
