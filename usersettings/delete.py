from flask import session, Blueprint, request, flash, redirect, url_for, render_template

from database.db import db
from database.models import User, Apikey
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
                # delete all associated API-Keys:
                db.session.query(Apikey).filter(Apikey.owner_id == user_id).delete()
                db.session.commit()

                # delete the user from the database
                db.session.delete(user)
                db.session.commit()
                session.pop('user_id', None)
                flash('Your account has been deleted.', 'info')
                return redirect(url_for('main_page.main_index'))
            else:
                flash('Deletion Token not (or no longer) valid, if you tried to delete your account, please try again.',
                      'error')
                return render_template('delete.html', token=user.get_account_deletion_token())
        else:
            flash('Unknown error, could not find User in Database. Account already deleted?', 'warning')
            return redirect(url_for('main_page.main_index'))
    else:
        # "Do you really want to delete your account? This action can not be undone <a hrf=.../delete?token=user.get_account_deletion_token()
        return render_template('delete.html', token=user.get_account_deletion_token())


"""
@delete.route('/delete')
@require_logged_in
def do_logout():
    # remove the username from the session if it is there
    if 'user_id' in session:
        session.pop('user_id', None)
        flash('You have successfully logged out', 'success')
    else:
        flash('You are already logged out', 'warning')
    return redirect(url_for('main_page.main_index'))
"""
