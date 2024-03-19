from dotenv import load_dotenv
from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

from config import DBConfig

load_dotenv()
config = DBConfig()

DB = PostgresEngine(
    config={
        "host": config.host,
        "database": config.name,
        "user": config.user,
        "port": config.port,
        "password": config.password,
    }
)

APP_REGISTRY = AppRegistry(apps=["lipotes.dictionary.piccolo_app"])
