from urllib.request import Request

from litestar import Litestar, Response, MediaType
from litestar.logging import StructLoggingConfig
from litestar.contrib.sqlalchemy.plugins import SQLAlchemySerializationPlugin
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

from app.controller import index
from app.controller.dict import get_dictionaries
from app.db.connection import db_connection, provide_transaction

logging_config = StructLoggingConfig()


def plain_text_exception_handler(_: Request, exc: Exception) -> Response:
    """Default handler for exceptions subclassed from HTTPException."""
    status_code = getattr(exc, "status_code", HTTP_500_INTERNAL_SERVER_ERROR)
    detail = getattr(exc, "detail", "")
    print(exc)

    return Response(
        media_type=MediaType.TEXT,
        content=detail,
        status_code=status_code,
    )


app = Litestar(
    logging_config=logging_config,
    lifespan=[db_connection], # noqa
    plugins=[SQLAlchemySerializationPlugin()],
    dependencies={"tx": provide_transaction},
    exception_handlers={
        Exception: plain_text_exception_handler,
    },
    route_handlers=[
        index,
        # api,
        get_dictionaries,
    ],
)
