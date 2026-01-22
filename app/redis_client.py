import redis
from .config import settings

# Create the connection to the cloud
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=int(settings.REDIS_PORT),
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5
)

# Simple test function
def check_redis():
    try:
        r.ping()
        return True
    except redis.ConnectionError:
        return False