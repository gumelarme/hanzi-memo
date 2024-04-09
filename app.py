import os
import time

from litestar import Litestar, MediaType, Request, Response, Router
from litestar.config.cors import CORSConfig
from litestar.contrib.sqlalchemy.plugins import SQLAlchemySerializationPlugin
from litestar.exceptions import HTTPException
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy.orm.exc import NoResultFound

from config.log import logging_config
from lipotes.db.connection import db_connection, provide_transaction
from lipotes.route import api
from lipotes.startup import startup_functions


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

timer = {}


async def before(request: Request) -> None:
    timer[request.get_session_id()] = time.process_time_ns()


async def after(request: Request):
    start_time = timer[request.get_session_id()]

    ms_time = (time.process_time_ns() - start_time) / 1_000_000
    request.logger.info("Request done", time=f"{ms_time}ms")


app = Litestar(
    lifespan=[db_connection],  # noqa
    plugins=[
        SQLAlchemySerializationPlugin(),
        StructlogPlugin(config=StructlogConfig(logging_config)),
    ],
    dependencies={"tx": provide_transaction},
    middleware=[rate_limit_config.middleware],
    cors_config=cors,
    on_startup=startup_functions,
    before_request=before,
    after_response=after,
    exception_handlers={
        Exception: json_logger_exception_handler,
    },
    route_handlers=[
        Router(path="/api/v1", route_handlers=api),
    ],
)
