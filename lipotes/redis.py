import os

import fakeredis
import redis
from dotenv import load_dotenv

from config.redis import RedisConfig

load_dotenv()
config = RedisConfig()

APP_ENV = os.environ.get("APP_ENV", "DEV")
__pool = redis.ConnectionPool(
    host=config.host,
    port=config.port,
    max_connections=config.max_connections,
    username=config.username,
    password=config.password,
    db=config.db,
    decode_responses=True,
)


# TODO: use dependency injection by litestar instead
def get_pool():
    if APP_ENV == "TEST":
        # Always return new fake connections on test,
        # so that pytest parametrize doesn't use previous cache
        return redis.ConnectionPool(
            connection_class=fakeredis.FakeConnection,
            server=fakeredis.FakeServer(),
        )

    return __pool
