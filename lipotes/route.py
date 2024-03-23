from litestar import get

from lipotes.text.controller import TextController


@get("/")
async def index() -> dict[str, any]:
    return {"data": "Hello, this is lipotes"}


api = [
    index,
    TextController,
]
