import logging

import structlog
from litestar import Litestar, MediaType, Request, Response
from litestar.contrib.sqlalchemy.plugins import SQLAlchemySerializationPlugin
from litestar.exceptions import HTTPException
from litestar.logging import StructLoggingConfig
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

from app.controller import index
from app.controller.collection import CollectionController
from app.controller.dict import DictionaryController
from app.controller.lexeme import LexemeController
from app.controller.pinyin import get_pinyin
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


def plain_text_exception_handler(request: Request, exc: Exception) -> Response:
    """Default handler for exceptions subclassed from HTTPException."""
    status_code = getattr(exc, "status_code", HTTP_500_INTERNAL_SERVER_ERROR)
    detail = getattr(exc, "detail", "")

    if not isinstance(exc, HTTPException):
        request.logger.exception(exc)
    request.logger.error(exc)

    return Response(
        media_type=MediaType.TEXT,
        content=detail,
        status_code=status_code,
    )


app = Litestar(
    logging_config=logging_config,
    lifespan=[db_connection],  # noqa
    plugins=[SQLAlchemySerializationPlugin()],
    dependencies={"tx": provide_transaction},
    exception_handlers={
        Exception: plain_text_exception_handler,
    },
    route_handlers=[
        index,
        get_pinyin,
        CollectionController,
        LexemeController,
        DictionaryController,
    ],
)
