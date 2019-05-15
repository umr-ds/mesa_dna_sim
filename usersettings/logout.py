from flask import Blueprint, session, redirect, url_for, flash

from usersettings.login import require_logged_in

logout = Blueprint("logout", __name__, template_folder="templates")


@logout.route('/logout')
@require_logged_in
def do_logout():
    # remove the username from the session if it is there
    if 'user_id' in session:
        session.pop('user_id', None)
        flash('You have successfully logged out', 'success')
    else:
        flash('You are already logged out', 'warning')
    return redirect(url_for('main_page.main_index'))
