import os

from redis import Redis

from config import redis_ip

redis = Redis(host=(os.environ.get('REDIS_SERVER') or redis_ip))
