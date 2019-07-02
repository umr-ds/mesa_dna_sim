import json
import re

from flask import Blueprint, render_template, redirect, session, request, flash, url_for, jsonify
from sqlalchemy import desc, or_, and_
from sqlalchemy.orm import Query

from api.RateLimit import ratelimit, get_view_rate_limit
from api.apikey import require_apikey
from database.db import db
from database.models import User, Apikey, UndesiredSubsequences, ErrorProbability, SynthesisErrorRates, \
    SynthesisErrorCorrection, SynthesisMethods
from usersettings.login import require_logged_in, check_password
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
    undesired_sub_seq = UndesiredSubsequences.query.filter(
        or_(UndesiredSubsequences.owner_id == user_id, UndesiredSubsequences.validated == True)).order_by(
        desc(UndesiredSubsequences.id)).all()
    gc_charts = ErrorProbability.query.filter(
        and_(or_(ErrorProbability.user_id == user_id, ErrorProbability.validated == True),
             ErrorProbability.type == "gc")).order_by(desc(ErrorProbability.id)).all()
    homopolymer_charts = ErrorProbability.query.filter(
        and_(or_(ErrorProbability.user_id == user_id, ErrorProbability.validated == True),
             ErrorProbability.type == "homopolymer")).order_by(desc(ErrorProbability.id)).all()
    if request.method == "POST":
        sequence = request.json.get('sequence')
        return render_template('sequence_view.html', apikey=apikey_obj.apikey, sequence=sequence,
                               usubsequence=undesired_sub_seq,
                               gc_charts=[ErrorProbability.serialize(x, int(user_id)) for x in gc_charts],
                               homopolymer_charts=[ErrorProbability.serialize(x, int(user_id)) for x in
                                                   homopolymer_charts])
    else:
        sequence = request.args.get('sequence')
        return render_template('sequence_view.html', apikey=apikey_obj.apikey, sequence=sequence, host=request.host,
                               usubsequence=undesired_sub_seq,
                               gc_charts=[ErrorProbability.serialize(x, int(user_id)) for x in gc_charts],
                               homopolymer_charts=[ErrorProbability.serialize(x, int(user_id)) for x in
                                                   homopolymer_charts])


@main_page.route("/undesired_subsequences", methods=['GET', 'POST'])
@require_logged_in
def undesired_subsequences():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    if user_id and user:
        undesired_sub_seq = UndesiredSubsequences.query.filter_by(owner_id=user_id).order_by(
            desc(UndesiredSubsequences.id)).all()
        res = db.session.query(SynthesisErrorRates).filter(
            or_(SynthesisErrorRates.user_id == user_id, SynthesisErrorRates.validated.is_(True))).order_by(
            desc(SynthesisErrorRates.id)).all()
        out = [x.as_dict() for x in res]
        id_out = {}
        default_eobj = {'id': 'new', 'name': 'New'}
        for x in out:
            # x['err_attributes'] = json.loads(x['err_attributes'].replace("'", '"'))
            # x['err_data'] = json.loads(x['err_data'].replace("'", '"'))
            id_out[int(x['id'])] = x
        return render_template('undesired_subsequences.html', synthesis_errors=id_out, usubsequence=undesired_sub_seq,
                               default_eobj=default_eobj, host=request.host)
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


@main_page.route("/api/update_subsequence", methods=['POST'])
@require_logged_in
def update_subsequences():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    sequence_id = request.form.get('sequence_id')
    sequence = sanitize_input(request.form.get('sequence'))
    error_prob = request.form.get('error_prob')
    description = sanitize_input(request.form.get('description'), r'[^a-zA-Z0-9() ]')
    if user_id and user and sequence_id is not None and sequence is not None and sequence != "" and error_prob is not None:
        try:
            error_prob = float(error_prob)
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
                 'description': curr_sub_seq.description})
        except:
            return jsonify({'did_succeed': False})
    else:
        return jsonify({'did_succeed': False})


@main_page.route("/api/update_error_prob_charts", methods=['POST'])
@require_logged_in
def update_error_prob_charts():
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
@require_logged_in
def get_error_prob_charts():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    if request.method == "POST":
        typ = request.json.get('type')
    else:
        typ = request.args.get('type')
    try:
        if user_id and user and typ is not None:
            charts = ErrorProbability.query.filter(
                and_(or_(ErrorProbability.user_id == user_id, ErrorProbability.validated is True),
                     ErrorProbability.type == typ)).order_by(desc(ErrorProbability.id)).all()

            return jsonify(
                {'did_succeed': True, 'charts': [ErrorProbability.serialize(x, int(user_id)) for x in charts]})
        else:
            return jsonify({'did_succeed': False})
    except Exception as x:
        return jsonify({'did_succeed': False})


@main_page.route("/api/get_error_probs", methods=['GET', 'POST'])
@require_logged_in
def get_synth_error_probs():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    if request.method == "POST":
        req = request.json
    else:
        req = request.args
    flat = "flat" in req and bool(req["flat"])
    try:
        if user_id and user:
            res = db.session.query(SynthesisErrorRates).filter(
                or_(SynthesisErrorRates.user_id == user_id, SynthesisErrorRates.validated.is_(True))).order_by(
                desc(SynthesisErrorRates.id)).all()
            methods = [x.as_dict() for x in SynthesisMethods.query.all()]
            # res = db.session.query(SynthesisErrorCorrection.data.label("name"),
            #                       SynthesisMethods.method.label("category"), SynthesisErrorRates.err_data,
            #                       SynthesisErrorRates.err_attributes, SynthesisErrorRates.validated).join(
            #    SynthesisErrorCorrection).join(SynthesisMethods).filter(
            #    or_(SynthesisErrorRates.user_id == user_id, SynthesisErrorRates.validated.is_(True))).order_by(
            #    desc(SynthesisErrorRates.id)).all()
            tmp = [x.as_dict() for x in res]
            res = dict()
            for x in tmp:
                # x['err_attributes'] = json.loads(x['err_attributes'].replace("'", '"'))
                # x['err_data'] = json.loads(x['err_data'].replace("'", '"'))
                id = int(x['method_id']) - 1
                meth_str = methods[id].get('method')
                if meth_str not in res:
                    res[meth_str] = []
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
                res[meth_str].append(x)
            return jsonify(
                {'did_succeed': True, 'res': res, 'methods': methods})
        else:
            return jsonify({'did_succeed': False})
    except Exception as x:
        # raise x
        return jsonify({'did_succeed': False})


@main_page.route("/api/add_error_probs", methods=['GET', 'POST'])
@require_logged_in
def add_synth_error_probs():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    synth_conf_str = request.json.get('synth_conf')
    if user_id and user and synth_conf_str is not None:
        try:
            synth_conf = json.loads(synth_conf_str)
            err_data = synth_conf['err_data']
            err_attributes = synth_conf['err_attributes']
            name = sanitize_input(synth_conf['name'])

            new_synth = SynthesisErrorRates(method_id=0, user_id=user_id, validated=False, name=name,
                                            err_data=err_data, err_attributes=err_attributes)

            db.session.add(new_synth)
            db.session.commit()
            return render_template('error_probs.html', e_obj=new_synth.as_dict())
        except Exception as x:
            return jsonify({'did_succeed': False})
    return jsonify({'did_succeed': False})


@main_page.route("/api/update_error_probs", methods=['GET', 'POST'])
@require_logged_in
def update_synth_error_probs():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    synth_conf_str = request.json.get('synth_conf')
    if user_id and user and synth_conf_str is not None:
        try:
            synth_conf = json.loads(synth_conf_str)
            err_data = synth_conf['err_data']
            err_attributes = synth_conf['err_attributes']
            name = sanitize_input(synth_conf['name'])
            copy = bool(request.json.get('copy'))
            id = int(synth_conf['id'])
            curr_synth = ErrorProbability.query.filter_by(user_id=user_id, id=id).first()

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


def sanitize_input(input, regex=r'[^a-zA-Z0-9()]'):
    result = re.sub(regex, "", input)
    return result
