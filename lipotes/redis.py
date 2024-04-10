import redis
from dotenv import load_dotenv

from config.redis import RedisConfig

load_dotenv()
config = RedisConfig()

pool = redis.ConnectionPool(
    host=config.host,
    port=config.port,
    max_connections=config.max_connections,
    username=config.username,
    password=config.password,
    db=config.db,
    decode_responses=True,
)
