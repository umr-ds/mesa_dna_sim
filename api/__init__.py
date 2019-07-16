import os

from redis import Redis

redis = Redis(host=(os.environ.get('REDIS_SERVER') or '172.24.0.3'))
