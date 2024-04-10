from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    host: str
    port: int
    password: str
    username: Optional[str] = None
    db: int = 0
    max_connections: int = 20

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="REDIS_",
    )
