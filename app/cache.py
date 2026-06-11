import redis
from app.config import settings

# Initialize a connection pool natively on your machine
redis_pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis_client() -> redis.Redis:
    """
    Dependency provider or utility function to obtain 
    a fast context client connection from the shared pool.
    """
    return redis.Redis(connection_pool=redis_pool)
