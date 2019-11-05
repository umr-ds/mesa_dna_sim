import datetime
import math
import re
import time

from flask import Blueprint, render_template, redirect, session, request, flash, url_for, jsonify, send_from_directory, \
    current_app
from flask_cors import cross_origin
from jinja2 import evalcontextfilter
from sqlalchemy import desc, or_, and_, asc

from api.mail import send_mail
from api.RateLimit import ratelimit, get_view_rate_limit
from api.apikey import require_apikey, create_apikey
from database.db import db
from database.models import User, Apikey, UndesiredSubsequences, ErrorProbability, SynthesisErrorRates, \
    MethodCategories, SequencingErrorRates, PcrErrorRates, StorageErrorRates
from usersettings.delete import removeUser
from usersettings.login import require_logged_in, check_password, require_admin
from usersettings.register import gen_password
from api.RedisStorage import get_keys, get_expiration_time, set_expiration_time, read_from_redis, read_all_from_redis

main_page = Blueprint("main_page", __name__, template_folder="templates")


@main_page.route("/")
def main_index():
    if check_existing_users():
        return redirect(url_for("main_page.setup"))
    return render_template('index.html'), 200


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


def check_existing_users():
    users = User.query.all()
    return len(users) == 1 and users[0].user_id == 0


@main_page.route("/setup", methods=["GET", "POST"])
def setup():
    if check_existing_users():
        if request.method == "GET":
            return render_template("initial_setup.html"), 200
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            new_admin = User(email=email, password=gen_password(password),
                             created=int(time.time()),
                             validated=True, is_admin=True)
            db.session.add(new_admin)
            db.session.commit()
            create_apikey(new_admin.user_id)
            session['user_id'] = new_admin.user_id
            flash("Admin-Account created. Enjoy the Software.", 'info')
            return redirect(url_for("main_page.main_index"))
    else:
        return redirect(url_for("main_page.main_index"))


@main_page.route("/manage_users", methods=["GET", "POST"])
@require_logged_in
@require_admin
def manage_users():
    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args
    if request.method == "GET":
        return jsonify([User.serialize(x) for x in User.query.all()])
    else:
        user_id = r_method.get('user_id')
        do_delete = 'do_delete' in r_method and bool(r_method.get('do_delete'))
        do_update = 'do_update' in r_method and bool(r_method.get('do_update'))
        user = User.query.filter_by(user_id=user_id).first()
        all_admins = User.query.filter_by(is_admin=True).all()
        if do_delete and not do_update:
            if user.is_admin and len(all_admins) == 1:
                # we can not allow deletion of the last admin account!
                return jsonify({'did_succeed': False})
            return jsonify({'did_succeed': removeUser(user)})
        elif do_update:
            new_email = r_method.get('new_email')
            validated = bool(r_method.get('validated'))
            is_admin = bool(r_method.get('is_admin'))
            user.email = new_email
            user.validated = validated
            user.is_admin = is_admin
            db.session.add(user)
            db.session.commit()
            keys = Apikey.query.filter_by(owner_id=user.user_id).all()
            if len(keys) == 0 and user.validated:
                create_apikey(user.user_id)
            return jsonify({'did_succeed': True})
        return jsonify({'did_succeed': False})


@main_page.route("/admin", methods=["GET"])
# @require_logged_in
@require_admin
def adminpage():
    today = math.floor(time.time())
    prev_results = sorted([(str(x).split("_")[1], int(str(x).split("_")[2][:-1]),
                     today * 1000 + get_expiration_time(x)) for x in get_keys('USER_*-*')], key=lambda x: x[2], reverse=True)[0:50]
    undesired_sub_seq = db.session.query(UndesiredSubsequences).filter(
        or_(UndesiredSubsequences.awaits_validation.is_(True), UndesiredSubsequences.validated.is_(True))).order_by(
        asc(UndesiredSubsequences.id)).all()
    graph_errors = db.session.query(ErrorProbability).filter(
        or_(ErrorProbability.awaits_validation.is_(True), ErrorProbability.validated.is_(True))).order_by(
        asc(ErrorProbability.id)).all()
    # ErrorProbability
    res = db.session.query(SynthesisErrorRates).filter(
        or_(SynthesisErrorRates.awaits_validation.is_(True), SynthesisErrorRates.validated.is_(True))).order_by(
        asc(SynthesisErrorRates.id)).all()
    out = [x.as_dict() for x in res]
    id_out = {}
    default_eobj = {'id': 'new', 'name': 'New', 'err_attributes': {'mismatch': {}}}
    for x in out:
        id_out[int(x['id'])] = x

    seq_res = db.session.query(SequencingErrorRates).filter(
        or_(SequencingErrorRates.awaits_validation.is_(True), SequencingErrorRates.validated.is_(True))).order_by(
        asc(SequencingErrorRates.id)).all()
    seq_out = [x.as_dict() for x in seq_res]
    seq_id_out = {}
    for x in seq_out:
        seq_id_out[int(x['id'])] = x

    pcr_res = db.session.query(PcrErrorRates).filter(
        or_(PcrErrorRates.awaits_validation.is_(True), PcrErrorRates.validated.is_(True))).order_by(
        asc(PcrErrorRates.id)).all()
    pcr_out = [x.as_dict() for x in pcr_res]
    pcr_id_out = {}
    for x in pcr_out:
        pcr_id_out[int(x['id'])] = x

    storage_res = db.session.query(StorageErrorRates).filter(
        or_(StorageErrorRates.awaits_validation.is_(True), StorageErrorRates.validated.is_(True))).order_by(
        asc(StorageErrorRates.id)).all()
    storage_out = [x.as_dict() for x in storage_res]
    storage_id_out = {}
    for x in storage_out:
        storage_id_out[int(x['id'])] = x

    users = User.query.order_by(
        asc(User.user_id)).all()

    types = MethodCategories.query.order_by(asc(MethodCategories.method)).all()

    return render_template('admin_page.html', synthesis_errors=id_out, sequencing_errors=seq_id_out,
                           storage_errors=storage_id_out, pcr_errors=pcr_id_out,
                           graph_errors=graph_errors, usubsequence=undesired_sub_seq, default_eobj=default_eobj,
                           host=request.url_root, users=users, prev_results=prev_results, types=types), 200


@main_page.route('/history', methods=['GET'])
@require_logged_in
def history():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    is_admin = user.is_admin
    amount = min(50, int(request.args.get('amount', 50)))
    offset = int(request.args.get('offset', 0))
    all = bool('all' in request.args)

    tmp = get_keys('USER_*-*_' + str(user_id))
    if offset > len(tmp):
        return jsonify([])
    if offset+amount > len(tmp):
        amount = len(tmp)-offset
    if all:
        offset = 0
        amount = len(tmp)
    prev_results = sorted([(str(x).split("_")[1], (int(str(x).split("_")[2][:-1]) if is_admin else None),
                     time.time() * 1000 + get_expiration_time(x)) for x in tmp], key=lambda x: x[2], reverse=True)[offset:offset+amount]
    return jsonify(prev_results)

@main_page.route('/profile', methods=["GET", "POST"])
# @require_apikey
# @ratelimit(limit=300, per=60 * 15)
@require_logged_in
def profile():
    """
    Manages profile settings, e.g. changing the password or email. Also shows the users apikey.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    today = time.time()
    prev_results = sorted([(str(x).split("_")[1], int(str(x).split("_")[2][:-1]),
                            today * 1000 + get_expiration_time(x)) for x in get_keys('USER_*-*_' + str(user_id))],
                          key=lambda x: x[2], reverse=True)[0:50]
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
        return render_template('profile.html', apikeys=keys, current_email=user.email, prev_results=prev_results)
    return render_template('profile.html')


@main_page.route('/rate-limited')
@require_apikey
@ratelimit(limit=300, per=60 * 15)
def index():
    return '<h1>This is a rate limited response</h1>'


@main_page.route("/query_sequence", methods=['GET', 'POST'])
# @require_logged_in
def query_sequence():
    """
    The simulation main page.
    :return:
    """
    user_id = session.get('user_id')
    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args
    sequence = r_method.get('sequence')
    r_uid = r_method.get('uuid')
    if user_id is None:
        flash("Please log in to use all available features!", 'warning')
        apikey = Apikey.query.filter_by(owner_id=0).first().apikey
    else:
        user_id = int(user_id)
        apikey = Apikey.query.filter_by(owner_id=user_id).first()
        if apikey is not None:
            apikey = apikey.apikey
        else:
            apikey = "NO APIKEY ACTIVE!"
    undesired_sub_seq = UndesiredSubsequences.query.filter(
        or_(UndesiredSubsequences.owner_id == user_id, UndesiredSubsequences.validated == True)).order_by(
        asc(UndesiredSubsequences.id)).all()
    gc_charts = ErrorProbability.query.filter(
        and_(or_(ErrorProbability.user_id == user_id, ErrorProbability.validated == True),
             ErrorProbability.type == "gc")).order_by(asc(ErrorProbability.id)).all()
    homopolymer_charts = ErrorProbability.query.filter(
        and_(or_(ErrorProbability.user_id == user_id, ErrorProbability.validated == True),
             ErrorProbability.type == "homopolymer")).order_by(asc(ErrorProbability.id)).all()
    return render_template('sequence_view.html', apikey=apikey, sequence=sequence, host=request.url_root,
                           usubsequence=undesired_sub_seq, user_id=user_id, uuid=r_uid,
                           gc_charts=[ErrorProbability.serialize(x, user_id) for x in gc_charts],
                           homopolymer_charts=[ErrorProbability.serialize(x, user_id) for x in
                                               homopolymer_charts], mail_enabled=current_app.config['MAIL_ENABLED'])


@main_page.route("/settings", methods=['GET', 'POST'])
@require_logged_in
def undesired_motifs():
    """
    Configuration of the undesired subsequences in the Simulation Settings.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    if user_id and user:
        undesired_sub_seq = UndesiredSubsequences.query.filter_by(owner_id=user_id).order_by(
            asc(UndesiredSubsequences.id)).all()
        res = db.session.query(SynthesisErrorRates).filter(
            or_(SynthesisErrorRates.user_id == user_id, SynthesisErrorRates.validated.is_(True))).order_by(
            asc(SynthesisErrorRates.id)).all()
        out = [x.as_dict() for x in res]
        id_out = {}
        default_eobj = {'id': 'new', 'name': 'New', 'err_attributes': {'mismatch': {}}}
        for x in out:
            id_out[int(x['id'])] = x

        seq_res = db.session.query(SequencingErrorRates).filter(
            or_(SequencingErrorRates.user_id == user_id, SequencingErrorRates.validated.is_(True))).order_by(
            asc(SequencingErrorRates.id)).all()
        seq_out = [x.as_dict() for x in seq_res]
        seq_id_out = {}
        for x in seq_out:
            seq_id_out[int(x['id'])] = x

        pcr_res = db.session.query(PcrErrorRates).filter(
            or_(PcrErrorRates.user_id == user_id, PcrErrorRates.validated.is_(True))).order_by(
            asc(PcrErrorRates.id)).all()
        pcr_out = [x.as_dict() for x in pcr_res]
        pcr_id_out = {}
        for x in pcr_out:
            pcr_id_out[int(x['id'])] = x

        storage_res = db.session.query(StorageErrorRates).filter(
            or_(StorageErrorRates.user_id == user_id, StorageErrorRates.validated.is_(True))).order_by(
            asc(StorageErrorRates.id)).all()
        storage_out = [x.as_dict() for x in storage_res]
        storage_id_out = {}
        for x in storage_out:
            storage_id_out[int(x['id'])] = x

        return render_template('undesired_motifs.html', synthesis_errors=id_out, sequencing_errors=seq_id_out,
                               pcr_errors=pcr_id_out, storage_errors=storage_id_out,
                               usubsequence=undesired_sub_seq, default_eobj=default_eobj, host=request.url_root)
    else:
        flash("Could not find user, please login again", 'warning')
        session.pop('user_id')
        return render_template("index.html"), 200


@main_page.route("/api/delete_subsequence", methods=['POST'])
@require_logged_in
def delete_subsequences():
    """
    Deletion of undesired subsequences in the Simulation Settings.
    :return:
    """
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
    """
    Adding new undesired subsequences in the Simulation Settings.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    sequence = sanitize_input(request.form.get('sequence'))
    error_prob = max(0.0, min(1.0, float(request.form.get('error_prob'))))
    description = sanitize_input(request.form.get('description'))
    if user_id and user and sequence is not None and sequence != "" and error_prob is not None:
        try:
            error_prob = float(error_prob)
            new_subsequence = UndesiredSubsequences(sequence=sequence, error_prob=error_prob, validated=False,
                                                    owner_id=user_id, description=description)
            db.session.add(new_subsequence)
            db.session.commit()
            return jsonify(
                {'did_succeed': True, 'sequence': new_subsequence.sequence, 'error_prob': new_subsequence.error_prob,
                 'id': new_subsequence.id, 'created': new_subsequence.created, 'validated': new_subsequence.validated,
                 'description': new_subsequence.description})
        except:
            return jsonify({'did_succeed': False})
    else:
        return jsonify({'did_succeed': False})


@main_page.route("/api/validate_graph_error", methods=["POST"])
@require_logged_in
def request_validation_g_error():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    e_id = request.json.get('id')
    validation_desc = request.json.get('validation_desc')
    if user_id and user and e_id is not None:
        try:
            if user.is_admin:
                curr_error = ErrorProbability.query.filter_by(id=e_id).first()
                requesting_user = User.query.filter_by(user_id=curr_error.user_id).first()
                if requesting_user.user_id != user_id:
                    send_mail(None, requesting_user.email,
                              "Your Graph '" + curr_error.name + "' has been validated!",
                              subject="[MOSLA] Validation Request")
                curr_error.validated = True
            else:
                curr_error = ErrorProbability.query.filter_by(user_id=user_id, id=e_id).first()
                curr_error.validated = False
                curr_error.validation_desc = validation_desc
                send_mail(None, get_admin_mails(),
                          "The user " + str(user_id) + " (" + user.email + ") has requested a validation!",
                          subject="[MOSLA] Validation Request")
            curr_error.awaits_validation = curr_error.validated is False
            db.session.add(curr_error)
            db.session.commit()
            return jsonify(
                {'did_succeed': True, 'id': curr_error.id, 'validated': curr_error.validated,
                 'awaits_validation': curr_error.awaits_validation})
        except:
            return jsonify({'did_succeed': False})
    else:
        return jsonify({'did_succeed': False})


@main_page.route("/api/validate_custom_error", methods=["POST"])
@require_logged_in
def request_validation_c_error():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    error_method = request.json.get('method')
    validation_desc = request.json.get('validation_desc')
    try:
        q_class = \
            {'synth': SynthesisErrorRates, 'seq': SequencingErrorRates, 'pcr': PcrErrorRates,
             'storage': StorageErrorRates}[
                error_method]
    except:
        return jsonify({'did_succeed': False})
    e_id = request.json.get('id')
    if user_id and user and error_method is not None and e_id is not None:
        try:
            if user.is_admin:
                curr_error = db.session.query(q_class).filter_by(id=e_id).first()
                requesting_user = User.query.filter_by(user_id=curr_error.user_id).first()
                if requesting_user.user_id != user_id:
                    send_mail(None, [requesting_user.email],
                              "Your Error-Method '" + curr_error.name + "' has been validated!",
                              subject="[MOSLA] Validation Request")
                curr_error.validated = True
            else:
                curr_error = db.session.query(q_class).filter_by(user_id=user_id, id=e_id).first()
                curr_error.validated = False
                curr_error.validation_desc = validation_desc
                send_mail(None, get_admin_mails(),
                          "The user " + str(user_id) + " (" + user.email + ") has requested a validation!",
                          subject="[MOSLA] Validation Request")
            curr_error.awaits_validation = curr_error.validated is False
            db.session.add(curr_error)
            db.session.commit()
            return jsonify(
                {'did_succeed': True, 'id': curr_error.id, 'validated': curr_error.validated,
                 'awaits_validation': curr_error.awaits_validation})
        except Exception as ex:
            print(ex)
            return jsonify({'did_succeed': False})
    else:
        return jsonify({'did_succeed': False})


@main_page.route("/api/apply_for_validation_subsequence", methods=["POST"])
@require_logged_in
def apply_validation_subseq():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    sequence_id = request.form.get('sequence_id')
    validation_desc = sanitize_input(request.form.get('validation_desc'))
    if user_id and user and sequence_id is not None:
        try:
            if user.is_admin:
                curr_sub_seq = db.session.query(UndesiredSubsequences).filter_by(id=sequence_id).first()
                requesting_user = User.query.filter_by(user_id=curr_sub_seq.owner_id).first()
                if requesting_user.user_id != user_id:
                    send_mail(None, requesting_user.email,
                              "Your Motif / Subsequence '" + curr_sub_seq.description + "' has been validated!",
                              subject="[MOSLA] Validation Request")
                curr_sub_seq.validated = True
            else:
                curr_sub_seq = db.session.query(UndesiredSubsequences).filter_by(owner_id=user_id,
                                                                                 id=sequence_id).first()
                curr_sub_seq.validated = False
                curr_sub_seq.validation_desc = validation_desc
                send_mail(None, get_admin_mails(),
                          "The user " + str(user_id) + " (" + user.email + ") has requested a validation!",
                          subject="[MOSLA] Validation Request")
            curr_sub_seq.awaits_validation = curr_sub_seq.validated is False
            db.session.add(curr_sub_seq)
            db.session.commit()
            return jsonify(
                {'did_succeed': True, 'sequence': curr_sub_seq.sequence, 'error_prob': curr_sub_seq.error_prob,
                 'id': curr_sub_seq.id, 'created': curr_sub_seq.created, 'validated': curr_sub_seq.validated,
                 'description': curr_sub_seq.description, 'awaits_validation': curr_sub_seq.awaits_validation})
        except:
            return jsonify({'did_succeed': False})
    else:
        return jsonify({'did_succeed': False})


@main_page.context_processor
def utility_processor():
    def is_user_admin(user_id):
        try:
            user = User.query.filter_by(user_id=int(user_id)).first()
            return user.is_admin
        except:
            return False

    return dict(is_user_admin=is_user_admin)

@main_page.app_template_filter()
@evalcontextfilter
def to_ctime(eval_ctx, ms_time):
    try:
        return time.ctime(ms_time / 1000)
    except:
        return "NaN"

@main_page.route("/api/update_subsequence", methods=['POST'])
@require_logged_in
def update_subsequences():
    """
    Updating undesired subsequences in the Simulation Settings.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    sequence_id = request.form.get('sequence_id')
    sequence = sanitize_input(request.form.get('sequence'))
    error_prob = request.form.get('error_prob')
    description = sanitize_input(request.form.get('description'))
    if user_id and user and sequence_id is not None and sequence is not None and sequence != "" and error_prob is not None:
        try:
            error_prob = float(error_prob)
            if user.is_admin:
                curr_sub_seq = db.session.query(UndesiredSubsequences).filter_by(id=sequence_id).first()
            else:
                curr_sub_seq = db.session.query(UndesiredSubsequences).filter_by(owner_id=user_id,
                                                                                 id=sequence_id).first()
            curr_sub_seq.error_prob = error_prob
            curr_sub_seq.sequence = sequence
            curr_sub_seq.validated = False
            curr_sub_seq.description = description
            # db.session.add(curr_sub_seq)
            db.session.commit()
            return jsonify(
                {'did_succeed': True, 'sequence': curr_sub_seq.sequence, 'error_prob': curr_sub_seq.error_prob,
                 'id': curr_sub_seq.id, 'created': curr_sub_seq.created, 'validated': curr_sub_seq.validated,
                 'description': curr_sub_seq.description, 'awaits_validation': curr_sub_seq.awaits_validation})
        except:
            return jsonify({'did_succeed': False})
    else:
        return jsonify({'did_succeed': False})


@main_page.route("/api/update_error_prob_charts", methods=['POST'])
@require_logged_in
def update_error_prob_charts():
    """
    Updates an error probabilty graph.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    id = request.json.get('chart_id')
    jsonblob = request.json.get('jsonblob')  # .replace(">", "").replace("<", "")
    name = sanitize_input(request.json.get('name'), r'[^a-zA-Z0-9() ]')
    type = sanitize_input(request.json.get('type'), r'[^a-zA-Z0-9]')
    copy = bool(request.json.get('copy'))
    if user_id and user and id is not None and jsonblob is not None and jsonblob != "" and name is not None:
        try:
            # check if an entry exists for the given id AND user --> only entrys for the current user might be updated
            if user.is_admin:
                curr_error_prob = ErrorProbability.query.filter_by(id=id).first()
            else:
                curr_error_prob = ErrorProbability.query.filter_by(user_id=user_id, id=id).first()
            if curr_error_prob is None or copy:
                curr_error_prob = ErrorProbability(jsonblob=jsonblob, validated=False, name=name, user_id=user_id,
                                                   type=type)
                db.session.add(curr_error_prob)
            else:
                curr_error_prob.jsonblob = jsonblob
                curr_error_prob.validated = False
                curr_error_prob.name = name
                curr_error_prob.type = type
            db.session.commit()
            return jsonify(
                {'did_succeed': True, 'jsonblob': curr_error_prob.jsonblob, 'id': curr_error_prob.id,
                 'created': curr_error_prob.created, 'validated': curr_error_prob.validated,
                 'name': curr_error_prob.name, 'type': curr_error_prob.type})
        except Exception as ex:
            return jsonify({'did_succeed': False})
    else:
        return jsonify({'did_succeed': False})


@main_page.route("/api/delete_error_prob_charts", methods=['POST'])
@require_logged_in
def delete_error_prob_chart():
    """
    Deletes an error probabilty graph.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    chart_id = request.json.get('chart_id')
    try:
        if user_id and user and chart_id is not None:
            error_prob_chart = ErrorProbability.query.filter_by(user_id=user_id, id=chart_id).first()
            db.session.delete(error_prob_chart)
            db.session.commit()
            return jsonify({"did_succeed": True, "deleted_id": chart_id})
        else:
            return jsonify({"did_succeed": False, "deleted_id": chart_id})
    except:
        return jsonify({"did_succeed": False, "deleted_id": chart_id})


@main_page.route("/api/get_error_prob_charts", methods=['GET', 'POST'])
# @require_logged_in
def get_error_prob_charts():
    """
    Gets an error probability graph.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    if request.method == "POST":
        typ = request.json.get('type')
    else:
        typ = request.args.get('type')
    if typ is None:
        return jsonify({'did_succeed': False})
    try:
        if user_id and user:
            charts = ErrorProbability.query.filter(
                and_(or_(ErrorProbability.user_id == user_id, ErrorProbability.validated),
                     ErrorProbability.type == typ)).order_by(asc(ErrorProbability.id)).all()
        else:
            charts = ErrorProbability.query.filter(
                and_(ErrorProbability.validated, ErrorProbability.type == typ)).order_by(
                asc(ErrorProbability.id)).all()
        tmp_id = user_id
        if user_id is None:
            tmp_id = -1
        return jsonify(
            {'did_succeed': True, 'charts': [ErrorProbability.serialize(x, int(tmp_id)) for x in charts]})
    except Exception as x:
        return jsonify({'did_succeed': False})


@main_page.route("/api/get_error_probs", methods=['GET', 'POST'])
def get_synth_error_probs():
    """
    Gets synthesis error probabilities.
    :return:
    """
    user_id = session.get('user_id')
    if request.method == "POST":
        req = request.json
    else:
        req = request.args
    flat = "flat" in req and bool(req["flat"])
    try:
        # if user_id and user:
        methods = [x.as_dict() for x in MethodCategories.query.order_by(
            asc(MethodCategories.id)).all()]
        return jsonify(
            {'did_succeed': True, 'synth': get_error_probs_dict(SynthesisErrorRates, user_id, flat, methods),
             'seq': get_error_probs_dict(SequencingErrorRates, user_id, flat, methods),
             'pcr': get_error_probs_dict(PcrErrorRates, user_id, flat, methods),
             'storage': get_error_probs_dict(StorageErrorRates, user_id, flat, methods), 'methods': methods})
    except Exception as x:
        return jsonify({'did_succeed': False})


def get_error_probs_dict(error_model, user_id, flat, methods):
    """
    Generates a dictionary with error probabilities.
    :param error_model:
    :param user_id:
    :param flat:
    :param methods:
    :return:
    """
    db_result = db.session.query(error_model).filter(
        or_(error_model.user_id == user_id, error_model.validated.is_(True))).order_by(
        asc(error_model.id)).all()
    tmp = [x.as_dict() for x in db_result]
    db_result = dict()
    for x in tmp:
        id = int(x['method_id'])
        meth_str = methods[id].get('method')
        if meth_str not in db_result:
            db_result[meth_str] = []
        # x.pop('method_id')
        if x['name'] == "" or x['name'] is None:
            x['name'] = "None"
        x['is_owner'] = int(x['user_id']) == user_id
        if not flat:
            x.pop('user_id')
        else:
            x['method'] = methods
        x['id'] = int(x['id'])
        x['validated'] = bool(x['validated'])
        x['type'] = error_model.__name__.split("Error")[0].lower()
        db_result[meth_str].append(x)
    return db_result


@main_page.route("/api/add_<mode>_error_probs", methods=['GET', 'POST'])
@require_logged_in
def add_error_probs(mode):
    """
    Adds synthesis error probabilities.
    :return:
    """
    try:
        choose = \
            {'synth': SynthesisErrorRates, 'seq': SequencingErrorRates, 'pcr': PcrErrorRates,
             'storage': StorageErrorRates}[
                mode]
    except:
        return jsonify({'did_succeed': False})
    try:
        user_id = session.get('user_id')
        user = User.query.filter_by(user_id=user_id).first()
        data_conf = request.json.get('data')
        asHTML = request.json.get('asHTML')
        if user_id and user and data_conf is not None:
            err_data = floatify(data_conf['err_data'])
            err_attributes = floatify(data_conf['err_attributes'])
            name = sanitize_input(data_conf['name'])

            new_elem = choose(method_id=0, user_id=user_id, validated=False, name=name,
                              err_data=err_data, err_attributes=err_attributes)

            db.session.add(new_elem)
            db.session.commit()
            res = {'did_succeed': True, 'id': new_elem.id}

            if asHTML is not None and asHTML:
                res['content'] = render_template('error_probs.html', e_obj=new_elem.as_dict(), host=request.url_root,
                                                 mode=mode)
            else:
                res['content'] = new_elem.as_dict()
            return jsonify(res)
        return jsonify({'did_succeed': False})
    except Exception as x:
        return jsonify({'did_succeed': False})


def floatify(x, sanitize_mode=False):
    for key in x:
        if (key == "mismatch" and isinstance(x[key], dict)) or sanitize_mode:
            if isinstance(x[key], dict):
                x[key] = floatify(x[key], sanitize_mode=True)
            else:
                if not (isinstance(x[key], int) or isinstance(x[key], float)):
                    x[key] = sanitize_input(x[key])
        else:
            if isinstance(x[key], dict):
                x[key] = floatify(x[key], sanitize_mode=sanitize_mode)
            else:  # if isinstance(value, str):
                x[key] = float(x[key])
    return x


@main_page.route("/api/update_<mode>_error_probs", methods=['GET', 'POST'])
@require_logged_in
def update_synth_error_probs(mode):
    """
    Updates synthesis error probabilities.
    :return:
    """
    try:
        choose = \
            {'synth': SynthesisErrorRates, 'seq': SequencingErrorRates, 'pcr': PcrErrorRates,
             'storage': StorageErrorRates}[
                mode]
    except:
        return jsonify({'did_succeed': False})

    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    data_conf = request.json.get('data')
    if user_id and user and data_conf is not None:
        try:
            err_data = data_conf['err_data']
            err_attributes = data_conf['err_attributes']
            name = sanitize_input(data_conf['name'])
            copy = bool(request.json.get('copy'))
            id = int(data_conf['id'])
            m_id = 0
            try:
                m_id = int(data_conf['type'])
            except:
                m_id = 0
            if user.is_admin:
                curr_synth = choose.query.filter_by(id=id).first()
            else:
                curr_synth = choose.query.filter_by(user_id=user_id, id=id).first()

            if curr_synth is None or copy:
                curr_synth = choose(method_id=m_id, user_id=user_id, validated=False, name=name,
                                    err_data=err_data, err_attributes=err_attributes)
                db.session.add(curr_synth)
            else:
                curr_synth.validated = False
                curr_synth.name = name
                curr_synth.err_data = err_data
                curr_synth.err_attributes = err_attributes
                curr_synth.method_id = m_id
            db.session.commit()
            return jsonify({'did_succeed': True})
        except Exception as x:
            return jsonify({'did_succeed': False})
    return jsonify({'did_succeed': False})


@main_page.route("/api/delete_<mode>", methods=['POST'])
@require_logged_in
def delete_synth(mode):
    """
    Deletes synthesis method.
    :return:
    """
    try:
        choose = \
            {'synth': SynthesisErrorRates, 'seq': SequencingErrorRates, 'pcr': PcrErrorRates,
             'storage': StorageErrorRates}[
                mode]
    except:
        return jsonify({'did_succeed': False})

    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    synth_id = request.form.get('id')
    if user_id and user and synth_id is not None:
        try:
            synth_err_to_delete = choose.query.filter_by(user_id=user_id, id=synth_id).first()
            db.session.delete(synth_err_to_delete)
            db.session.commit()
            return jsonify({'did_succeed': True, 'deleted_id': synth_id})
        except Exception as ex:
            return jsonify({'did_succeed': False, 'deleted_id': synth_id})
    else:
        return jsonify({'did_succeed': False, 'deleted_id': synth_id})


@main_page.route('/swagger.json')
@cross_origin()
def send_js():
    return send_from_directory('', 'swagger.json')


def sanitize_input(input, regex=r'[^a-zA-Z0-9():/\\.,\-&?#= ]'):
    result = re.sub(regex, "", input)
    return result


def get_admin_mails():
    admins = User.query.filter_by(is_admin=True).all()
    return [x.mail for x in admins]


@require_admin
@main_page.route('/remove_result', methods=['POST'])
def remove_uuid():
    """
    Deletion of undesired subsequences in the Simulation Settings.
    :return:
    """
    r_method = request.json
    uuid = r_method.get('uuid')
    delete_all = r_method.get('delete_all')
    user_id = session.get('user_id')
    try:
        if uuid is None:
            raise Exception()
        do_delete = bool(r_method.get('do_delete'))
    except:
        return jsonify({'did_succeed': False, 'uuid': uuid}), 400
    user = User.query.filter_by(user_id=user_id).first()
    if user.is_admin and delete_all and do_delete:
        [set_expiration_time(x, 0) for x in get_keys('*')]
        return jsonify({'did_succeed': True, 'uuid': uuid})
    elif delete_all and do_delete:
        keys = get_keys('USER_*-*_' + str(user.user_id))
        keys = keys + [str(x).split("_")[1] for x in keys]
        [set_expiration_time(x, 0) for x in keys]
        return jsonify({'did_succeed': True, 'uuid': uuid})

    uuuid_user = read_from_redis('USER_' + uuid + "_" + str(user_id))
    if do_delete and uuuid_user is not None and (user.user_id == int(uuuid_user) or user.is_admin):
        # delete
        set_expiration_time(uuid, 0)
        set_expiration_time('USER_' + uuid + "_" + str(user_id), 0)
        return jsonify({'did_succeed': True, 'uuid': uuid})
    else:
        return jsonify({'did_succeed': False, 'uuid': uuid}), 400
