from redis import Redis, ConnectionPool
from config import redis_ip, redis_password

pool = ConnectionPool(host=redis_ip, password=redis_password, socket_timeout=10, retry_on_timeout=True)


def getRedis():
    return Redis(connection_pool=pool)
