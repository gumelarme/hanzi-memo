from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: int
    name: str = "hanzi_memo"
    debug: bool = False

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="DB_",
    )
