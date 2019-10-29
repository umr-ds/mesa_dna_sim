from redis import Redis
from config import redis_ip, redis_password

redis = Redis(host=redis_ip, password=redis_password)
