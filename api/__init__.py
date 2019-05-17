import os

from redis import Redis

redis = Redis(host=(os.environ.get('REDIS_SERVER') or 'redis'))
