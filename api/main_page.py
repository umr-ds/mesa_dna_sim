import json
import re

from flask import Blueprint, render_template, redirect, session, request, flash, url_for, jsonify
from sqlalchemy import desc, or_, and_, asc
from sqlalchemy.orm import Query

from api.RateLimit import ratelimit, get_view_rate_limit
from api.apikey import require_apikey
from database.db import db
from database.models import User, Apikey, UndesiredSubsequences, ErrorProbability, SynthesisErrorRates, \
    SynthesisErrorCorrection, MethodCategories, SequencingErrorRates, PcrErrorRates
from usersettings.login import require_logged_in, check_password, require_admin
from usersettings.register import gen_password

main_page = Blueprint("main_page", __name__, template_folder="templates")


#
# Since Flask will only be used for the API we will redirect to the main page
#
@main_page.route("/api")
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


@main_page.route("/", methods=["GET"])
def home():
    return render_template("index.html"), 200


@main_page.route("/admin", methods=["GET"])
# @require_logged_in
@require_admin
def adminpage():
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

    return render_template('admin_page.html', synthesis_errors=id_out, sequencing_errors=seq_id_out,
                           graph_errors=graph_errors, usubsequence=undesired_sub_seq, default_eobj=default_eobj,
                           host=request.url_root), 200


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
        apikey = Apikey.query.filter_by(owner_id=user_id).first().apikey
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
                                               homopolymer_charts])


@main_page.route("/settings", methods=['GET', 'POST'])
@require_logged_in
def undesired_subsequences():
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

        return render_template('undesired_subsequences.html', synthesis_errors=id_out, sequencing_errors=seq_id_out,
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
    error_prob = request.form.get('error_prob')
    description = sanitize_input(request.form.get('description'), r'[^a-zA-Z0-9() ]')
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
    # TODO add validation description!
    e_id = request.json.get('id')
    validation_desc = request.json.get('validation_desc')
    if user_id and user and e_id is not None:
        try:
            if user.is_admin:
                curr_error = ErrorProbability.query.filter_by(id=e_id).first()
                curr_error.validated = True
            else:
                curr_error = ErrorProbability.query.filter_by(user_id=user_id, id=e_id).first()
                curr_error.validated = False
                curr_error.validation_desc = validation_desc
            curr_error.awaits_validation = curr_error.validated is False
            # db.session.add(curr_error)
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
    # TODO add validation description!
    if error_method == "synth":
        q_class = SynthesisErrorRates
    else:
        q_class = SequencingErrorRates
    e_id = request.json.get('id')
    if user_id and user and error_method is not None and e_id is not None:
        try:
            if user.is_admin:
                curr_error = q_class.query.filter_by(id=e_id).first()
                curr_error.validated = True
            else:
                curr_error = q_class.query.filter_by(user_id=user_id, id=e_id).first()
                curr_error.validated = False
                curr_error.validation_desc = validation_desc
            curr_error.awaits_validation = curr_error.validated is False
            # db.session.add(curr_error)
            db.session.commit()
            return jsonify(
                {'did_succeed': True, 'id': curr_error.id, 'validated': curr_error.validated,
                 'awaits_validation': curr_error.awaits_validation})
        except:
            return jsonify({'did_succeed': False})
    else:
        return jsonify({'did_succeed': False})


@main_page.route("/api/apply_for_validation_subsequence", methods=["POST"])
@require_logged_in
def apply_validation_subseq():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    sequence_id = request.form.get('sequence_id')
    validation_desc = request.form.get('validation_desc')
    # sequence = sanitize_input(request.form.get('sequence'))
    # error_prob = request.form.get('error_prob')
    # description = sanitize_input(request.form.get('description'), r'[^a-zA-Z0-9() ]')
    if user_id and user and sequence_id is not None:
        try:
            if user.is_admin:
                curr_sub_seq = UndesiredSubsequences.query.filter_by(id=sequence_id).first()
                curr_sub_seq.validated = True
            else:
                curr_sub_seq = UndesiredSubsequences.query.filter_by(owner_id=user_id, id=sequence_id).first()
                curr_sub_seq.validated = False
                curr_sub_seq.validation_desc = validation_desc
            curr_sub_seq.awaits_validation = curr_sub_seq.validated is False
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


@main_page.context_processor
def utility_processor():
    def is_user_admin(user_id):
        try:
            user = User.query.filter_by(user_id=int(user_id)).first()
            return user.is_admin
        except:
            return False

    return dict(is_user_admin=is_user_admin)


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
    description = sanitize_input(request.form.get('description'), r'[^a-zA-Z0-9() ]')
    if user_id and user and sequence_id is not None and sequence is not None and sequence != "" and error_prob is not None:
        try:
            error_prob = float(error_prob)
            if user.is_admin:
                curr_sub_seq = UndesiredSubsequences.query.filter_by(id=sequence_id).first()
            else:
                curr_sub_seq = UndesiredSubsequences.query.filter_by(owner_id=user_id, id=sequence_id).first()
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
                and_(or_(ErrorProbability.user_id == user_id, ErrorProbability.validated is True),
                     ErrorProbability.type == typ)).order_by(asc(ErrorProbability.id)).all()
        else:
            charts = ErrorProbability.query.filter(
                and_(ErrorProbability.validated is True, ErrorProbability.type == typ)).order_by(
                asc(ErrorProbability.id)).all()
        return jsonify(
            {'did_succeed': True, 'charts': [ErrorProbability.serialize(x, int(user_id)) for x in charts]})

        # return jsonify({'did_succeed': False})
    except Exception as x:
        return jsonify({'did_succeed': False})


@main_page.route("/api/get_error_probs", methods=['GET', 'POST'])
# @require_logged_in
def get_synth_error_probs():
    """
    Gets synthesis error probabilities.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
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
             'seq': get_error_probs_dict(SequencingErrorRates, user_id, flat, methods), 'methods': methods})
        # else:
        #    return jsonify({'did_succeed': False})
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
            # x.pop('correction_id')
            x.pop('user_id')
        else:
            x['method'] = methods
        x['id'] = int(x['id'])
        x['validated'] = bool(x['validated'])
        db_result[meth_str].append(x)
    return db_result


@main_page.route("/api/add_seq_error_probs", methods=['GET', 'POST'])
@require_logged_in
def add_seq_error_probs():
    """
    Adds sequencing error probabilities.
    :return:
    """
    try:
        user_id = session.get('user_id')
        user = User.query.filter_by(user_id=user_id).first()
        synth_conf = request.json.get('data')
        asHTML = request.json.get('asHTML')
        if user_id and user and synth_conf is not None:

            # synth_conf = json.loads(synth_data)
            err_data = floatify(synth_conf['err_data'])
            err_attributes = floatify(synth_conf['err_attributes'])
            name = sanitize_input(synth_conf['name'])

            new_seq = SequencingErrorRates(method_id=0, user_id=user_id, validated=False, name=name,
                                           err_data=err_data, err_attributes=err_attributes)
            db.session.add(new_seq)
            db.session.commit()
            res = {'did_succeed': True, 'id': new_seq.id}

            if asHTML is not None and asHTML:
                res['content'] = render_template('error_probs.html', e_obj=new_seq.as_dict(), host=request.url_root,
                                                 mode='seq')
            else:
                res['content'] = new_seq.as_dict()
            return jsonify(res)
        return jsonify({'did_succeed': False})
    except Exception as x:
        raise x
        return jsonify({'did_succeed': False})


@main_page.route("/api/add_synth_error_probs", methods=['GET', 'POST'])
@require_logged_in
def add_synth_error_probs():
    """
    Adds synthesis error probabilities.
    :return:
    """
    try:
        user_id = session.get('user_id')
        user = User.query.filter_by(user_id=user_id).first()
        synth_conf = request.json.get('data')
        asHTML = request.json.get('asHTML')
        if user_id and user and synth_conf is not None:

            # synth_conf = json.loads(synth_data)
            err_data = floatify(synth_conf['err_data'])
            err_attributes = floatify(synth_conf['err_attributes'])
            name = sanitize_input(synth_conf['name'])

            new_synth = SynthesisErrorRates(method_id=0, user_id=user_id, validated=False, name=name,
                                            err_data=err_data, err_attributes=err_attributes)

            db.session.add(new_synth)
            db.session.commit()
            res = {'did_succeed': True, 'id': new_synth.id}

            if asHTML is not None and asHTML:
                res['content'] = render_template('error_probs.html', e_obj=new_synth.as_dict(), host=request.url_root,
                                                 mode='synth')
            else:
                res['content'] = new_synth.as_dict()
            return jsonify(res)
        return jsonify({'did_succeed': False})
    except Exception as x:
        raise x
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


@main_page.route("/api/update_synth_error_probs", methods=['GET', 'POST'])
@require_logged_in
def update_synth_error_probs():
    """
    Updates synthesis error probabilities.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    synth_conf = request.json.get('data')
    if user_id and user and synth_conf is not None:
        try:
            err_data = synth_conf['err_data']
            err_attributes = synth_conf['err_attributes']
            name = sanitize_input(synth_conf['name'])
            copy = bool(request.json.get('copy'))
            id = int(synth_conf['id'])
            if user.is_admin:
                curr_synth = SynthesisErrorRates.query.filter_by(id=id).first()
            else:
                curr_synth = SynthesisErrorRates.query.filter_by(user_id=user_id, id=id).first()

            if curr_synth is None or copy:
                curr_synth = SynthesisErrorRates(method_id=0, user_id=user_id, validated=False, name=name,
                                                 err_data=err_data, err_attributes=err_attributes)
                db.session.add(curr_synth)
            else:
                curr_synth.validated = False
                curr_synth.name = name
                curr_synth.err_data = err_data
                curr_synth.err_attributes = err_attributes
            db.session.commit()
            return jsonify({'did_succeed': True})
        except Exception as x:
            return jsonify({'did_succeed': False})
    return jsonify({'did_succeed': False})


@main_page.route("/api/delete_synth", methods=['POST'])
@require_logged_in
def delete_synth():
    """
    Deletes synthesis method.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    synth_id = request.form.get('synth_id')
    if user_id and user and synth_id is not None:
        try:
            synth_err_to_delete = SynthesisErrorRates.query.filter_by(user_id=user_id, id=synth_id).first()
            db.session.delete(synth_err_to_delete)
            db.session.commit()
            return jsonify({'did_succeed': True, 'deleted_id': synth_id})
        except Exception as ex:
            return jsonify({'did_succeed': False, 'deleted_id': synth_id})
    else:
        return jsonify({'did_succeed': False, 'deleted_id': synth_id})


@main_page.route("/api/delete_seq", methods=['POST'])
@require_logged_in
def delete_seq():
    """
    Deletes sequencing method.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    synth_id = request.form.get('synth_id')
    if user_id and user and synth_id is not None:
        try:
            seq_error_to_delete = SequencingErrorRates.query.filter_by(user_id=user_id, id=synth_id).first()
            db.session.delete(seq_error_to_delete)
            db.session.commit()
            return jsonify({'did_succeed': True, 'deleted_id': synth_id})
        except Exception as ex:
            return jsonify({'did_succeed': False, 'deleted_id': synth_id})
    else:
        return jsonify({'did_succeed': False, 'deleted_id': synth_id})


@main_page.route("/api/update_seq_error_probs", methods=['GET', 'POST'])
@require_logged_in
def update_seq_error_probs():
    """
    Updates sequencing error probabilities.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    synth_conf = request.json.get('data')
    if user_id and user and synth_conf is not None:
        try:
            err_data = synth_conf['err_data']
            err_attributes = synth_conf['err_attributes']
            name = sanitize_input(synth_conf['name'])
            copy = bool(request.json.get('copy'))
            id = int(synth_conf['id'])
            if user.is_admin:
                curr_seq = SequencingErrorRates.query.filter_by(id=id).first()
            else:
                curr_seq = SequencingErrorRates.query.filter_by(user_id=user_id, id=id).first()

            if curr_seq is None or copy:
                curr_seq = SequencingErrorRates(method_id=0, user_id=user_id, validated=False, name=name,
                                                err_data=err_data, err_attributes=err_attributes)
                db.session.add(curr_seq)
            else:
                curr_seq.validated = False
                curr_seq.name = name
                curr_seq.err_data = err_data
                curr_seq.err_attributes = err_attributes
            db.session.commit()
            return jsonify({'did_succeed': True})
        except Exception as x:
            return jsonify({'did_succeed': False})
    return jsonify({'did_succeed': False})


def sanitize_input(input, regex=r'[^a-zA-Z0-9()]'):
    result = re.sub(regex, "", input)
    return result
