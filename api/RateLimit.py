import time
from functools import update_wrapper
from flask import request, g

from . import getRedis
from api.apikey import is_admin_apikey


class RateLimit(object):
    expiration_window = 10

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = getRedis().pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)


def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)


def on_over_limit(limit):
    return 'You hit the rate limit', 400


def _request_api_key():
    return request.args.get('key') or (
        request.json and request.json.get('key')) or (
        request.form and request.form.get('key')) or request.headers.get('key')


def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.args.get('key'),
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            if is_admin_apikey(_request_api_key()):
                return f(*args, **kwargs)
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)

        return update_wrapper(rate_limited, f)

    return decorator
