from cachetools import LRUCache, cached
from litestar import Controller, get
from litestar.contrib.piccolo import PiccoloDTO
from litestar.exceptions import NotFoundException

from lipotes.collection.tables import Collection, LexemeCollection
from lipotes.dictionary.cache import LexemeCache
from lipotes.dictionary.tables import Lexeme


class CollectionController(Controller):
    path = "/collections"
    return_dto = PiccoloDTO[Collection]

    @get("/")
    async def get_collections(self) -> list[Collection]:
        return await Collection.objects().limit(10)

    @get("/{collection_id:int}", cache=True)
    async def get_collection_by_id(self, collection_id: int) -> Collection:
        result = await Collection.objects().get(Collection.id == collection_id)
        if result is None:
            raise NotFoundException()
        return result

    @get("/{collection_id:int}/lexemes", return_dto=PiccoloDTO[Lexeme], cache=True)
    async def get_lexemes_by_collection(self, collection_id: int) -> list[Lexeme]:
        lexemes = await (
            LexemeCollection.select(LexemeCollection.lexeme.id)
            .where(LexemeCollection.collection == collection_id)
            .output(as_list=True)
        )

        result = await Lexeme.find_multiple_by_id(lexemes)
        return [Lexeme(**x) for x in result]
