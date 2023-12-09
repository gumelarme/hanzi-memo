import logging
import os

import structlog
from litestar import Litestar, MediaType, Request, Response, Router
from litestar.config.cors import CORSConfig
from litestar.contrib.sqlalchemy.plugins import SQLAlchemySerializationPlugin
from litestar.exceptions import HTTPException
from litestar.logging import StructLoggingConfig
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy.orm.exc import NoResultFound

from app.controller import index
from app.controller.collection import CollectionController
from app.controller.dict import DictionaryController
from app.controller.lexeme import LexemeController
from app.controller.pinyin import get_pinyin
from app.controller.text import TextController
from app.db.connection import db_connection, provide_transaction

logging_config = StructLoggingConfig(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)


def json_logger_exception_handler(request: Request, exc: Exception) -> Response:
    """Default handler for exceptions subclassed from HTTPException."""
    status_code = getattr(exc, "status_code", HTTP_500_INTERNAL_SERVER_ERROR)
    detail = getattr(exc, "detail", "Internal Server Error")

    if isinstance(exc, HTTPException):
        request.logger.exception(str(exc))
    else:
        if isinstance(exc, NoResultFound):
            status_code = HTTP_404_NOT_FOUND
            detail = "resource not found"
            request.logger.error(str(exc))
        else:
            request.logger.exception(exc)

    res = Response(
        media_type=MediaType.JSON,
        content={
            "detail": detail,
            "status_code": status_code,
        },
        status_code=status_code,
    )

    if isinstance(exc, HTTPException):
        res.headers = exc.headers
        res.content["extra"] = exc.extra

    return res


rate = os.environ.get("APP_RATE_LIMIT", 1000)
rate_limit_config = RateLimitConfig(("minute", rate))
cors = CORSConfig()


app = Litestar(
    logging_config=logging_config,
    lifespan=[db_connection],  # noqa
    plugins=[SQLAlchemySerializationPlugin()],
    dependencies={"tx": provide_transaction},
    middleware=[rate_limit_config.middleware],
    cors_config=cors,
    exception_handlers={
        Exception: json_logger_exception_handler,
    },
    route_handlers=[
        Router(
            path="/api",
            route_handlers=[
                index,
                get_pinyin,
                CollectionController,
                LexemeController,
                DictionaryController,
                TextController,
            ],
        )
    ],
)
