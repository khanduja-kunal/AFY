import redis
from datetime import datetime
from fastapi import HTTPException, status
from app.core.config import REDIS_HOST, REDIS_PORT, MAX_DOWNLOADS_PER_DAY

# Redis client
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def check_rate_limit(ip: str):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    redis_key = f"downloads:{ip}:{today}"
    current = redis_client.get(redis_key)

    if current and int(current) >= MAX_DOWNLOADS_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    pipe = redis_client.pipeline()
    pipe.incr(redis_key, 1)
    if not current:
        pipe.expire(redis_key, 86400)  # 24 hours
    pipe.execute()
