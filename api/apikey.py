import time
from functools import wraps
import secrets

from flask import request, abort

from database.db import db
from database.models import Apikey


def query_apikey(key_):
    try:
        apikey = Apikey.query.filter_by(apikey=key_).first()
        return apikey is not None
    except Exception as e:
        print(e)
        return False  # str(e)


def require_apikey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        # todo dynamically check based on saved API-keys + ratelimit
        if (request.args.get('key') and query_apikey(request.args.get('key'))) or (
                request.json and request.json.get('key')) or (
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
