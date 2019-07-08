from . import redis


def save_to_redis(key, content, expiration_secs):
    p = redis.pipeline()
    p.set(key, content, expiration_secs)
    p.execute()


def read_from_redis(key):
    p = redis.pipeline()
    p.get(key)
    return p.execute()[0]