from flask import Blueprint, session, redirect, url_for, flash, make_response, current_app

from usersettings.login import require_logged_in

logout = Blueprint("logout", __name__, template_folder="templates")


@logout.route('/logout')
@require_logged_in
def do_logout():
    """
    Logs an user out and removes the username from the session if it's there.
    :return:
    """
    response = make_response(redirect(url_for('main_page.main_index')))
    if 'user_id' in session:
        session.clear()
        flash('You have successfully logged out', 'success')
        response.delete_cookie(current_app.session_cookie_name, path='/')
    else:
        flash('You are already logged out', 'warning')
    return response
