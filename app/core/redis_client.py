import redis
from app.core.config import CELERY_BROKER_URL

# Redis client setup
def get_redis_client():
    return redis.StrictRedis.from_url(CELERY_BROKER_URL, decode_responses=True)

# Celery will use this Redis client as the broker
