import time
from functools import wraps
import secrets
import traceback

from flask import request, abort, current_app

from database.db import db
from database.models import Apikey, User


def _get_admin_apikey():
    key = current_app.config.get('ADMIN_API_KEY')
    if isinstance(key, str):
        key = key.strip()
    return key or None


def is_admin_apikey(key_):
    admin_key = _get_admin_apikey()
    if not admin_key or not key_:
        return False
    return secrets.compare_digest(str(key_), admin_key)


def resolve_admin_owner_id():
    # Prefer a real admin account; during initial onboarding fall back to bootstrap user 0.
    admin = User.query.filter(User.is_admin.is_(True), User.user_id != 0).order_by(User.user_id.asc()).first()
    if admin is not None:
        return admin.user_id
    bootstrap_admin = User.query.filter_by(user_id=0).first()
    if bootstrap_admin is not None:
        return bootstrap_admin.user_id
    admin = User.query.filter_by(is_admin=True).order_by(User.user_id.asc()).first()
    if admin is not None:
        return admin.user_id
    return 0


def query_apikey(key_):
    try:
        if is_admin_apikey(key_):
            return True
        apikey = Apikey.query.filter_by(apikey=key_).first()
        return apikey is not None
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return False  # str(e)


def owner_for_key(key_):
    try:
        if is_admin_apikey(key_):
            return resolve_admin_owner_id()
        apikey = Apikey.query.filter_by(apikey=key_).first()
        if apikey is None:
            return False
        return apikey.owner_id
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return False  # str(e)


def require_apikey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        # todo dynamically check based on saved API-keys + ratelimit
        if (request.args.get('key') and query_apikey(request.args.get('key'))) or (
                request.json and request.json.get('key') and query_apikey(request.json.get('key'))) or (
                request.form and request.form.get('key') and query_apikey(request.form.get('key'))) or (
                request.headers.get('key') and query_apikey(request.headers.get('key'))):
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


def create_apikey(owner_id):
    """
    Creates an apikey for the user.
    :param owner_id: Id of the user
    :return: Apikey
    """
    while True:
        key = secrets.token_urlsafe(32)
        db_apikey = Apikey.query.filter_by(apikey=key).first()  # _or_404()
        if not db_apikey:
            break

    apikey = Apikey(created=int(time.time()), apikey=key, owner_id=owner_id)
    db.session.add(apikey)
    db.session.commit()
    return key
