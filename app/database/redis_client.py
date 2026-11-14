import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)


def test_redis_connection():
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False