from litestar import get


@get("/")
async def index() -> dict[str, any]:
    return {"data": "Hello, this is hanzi-memo"}
