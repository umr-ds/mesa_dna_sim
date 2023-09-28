from . import getRedis


def save_to_redis(key, content, expiration_secs, user=None):
    p = getRedis().pipeline()
    p.set(key, content, expiration_secs)
    if user is not None:
        p.set("USER_" + key + "_" + str(user), user, expiration_secs)
    p.execute()


def read_all_from_redis(key):
    p = getRedis().pipeline()
    if isinstance(key, list):
        for x in key:
            p.get(x)
    else:
        p.get(key)
    return p.execute()


def read_from_redis(key):
    return read_all_from_redis(key)[0]


def get_expiration_time(key):
    p = getRedis().pipeline()
    p.pttl(key)
    return p.execute()[0]


def set_expiration_time(key, time):
    p = getRedis().pipeline()
    p.expire(key, time)
    return p.execute()[0]


def get_keys(pattern):
    p = getRedis().pipeline()
    p.keys(pattern)
    return p.execute()[0]
