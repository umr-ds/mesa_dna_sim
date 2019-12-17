from flask import session, Blueprint, request, flash, redirect, url_for, render_template, make_response, current_app

from database.db import db
from database.models import User, Apikey, UndesiredSubsequences, ErrorProbability, SequencingErrorRates, \
    SynthesisErrorRates, StorageErrorRates, PcrErrorRates
from usersettings.login import require_logged_in

delete = Blueprint("delete", __name__, template_folder="templates")


@delete.route('/delete', methods=['GET', 'POST'])
@require_logged_in
def do_delete():
    """
    Deletes an user and the users apikeys permanently.
    :return:
    """
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()  # _or_404()
    if not user:
        flash('Could not perform action. Are you logged in?', 'error')
        return redirect(url_for('main_page.main_index'))

    if request.method == "POST":
        # You should really validate that these fields
        # are provided, rather than displaying an ugly
        # error message, but for the sake of a simple
        # example we'll just assume they are provided

        delete_token = request.form["token"]

        if user:
            if user.verify_account_deletion_token(delete_token):
                did_succeed = remove_user(user)
                if did_succeed:
                    session.pop('user_id', None)
                    flash('Your account has been deleted.', 'info')
                else:
                    flash('There has been an error, please try again or contact an administrator.', 'warning')
                response = make_response(redirect(url_for('main_page.main_index')))
                if did_succeed:
                    response.set_cookie('darkmode', 'false', 0)
                    response.set_cookie(current_app.session_cookie_name, '', 0)
                return response
            else:
                flash('Deletion Token not (or no longer) valid, if you tried to delete your account, please try again.',
                      'danger')
                return render_template('delete.html', token=user.get_account_deletion_token())
        else:
            flash('Unknown error, could not find User in Database. Account already deleted?', 'warning')
            return redirect(url_for('main_page.main_index'))
    else:
        # "Do you really want to delete your account? This action can not be undone <a hrf=.../delete?token=user.get_account_deletion_token()
        return render_template('delete.html', token=user.get_account_deletion_token())


def remove_user(user):
    if user.user_id == 0:
        # We do not allow deletion of User 0!
        return False
    user_id = user.user_id
    try:
        # delete all (custom) subsequences, synth, storage and sequencing rules from this user
        db.session.query(Apikey).filter(Apikey.owner_id == user_id).delete()
        db.session.query(UndesiredSubsequences).filter(UndesiredSubsequences.owner_id == user_id).delete()
        for table in [ErrorProbability, SequencingErrorRates, PcrErrorRates, StorageErrorRates,
                      SynthesisErrorRates]:
            db.session.query(table).filter(table.user_id == user_id).delete()
        db.session.commit()

        # delete the user from the database
        db.session.delete(user)
        db.session.commit()
        return True
    except Exception as ex:
        print(ex)
        return False

