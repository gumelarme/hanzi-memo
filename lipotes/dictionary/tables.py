from async_lru import alru_cache
from asyncache import cached
from cachetools import LRUCache
from piccolo.columns import ForeignKey, Serial, Varchar
from piccolo.table import Table

LEXEME_CACHE = LRUCache(maxsize=2**14)


class Lexeme(Table):
    id = Serial(primary_key=True)
    zh_sc = Varchar(null=True, required=True)
    zh_tc = Varchar(null=True, required=True)
    pinyin = Varchar(null=True, required=True)

    @classmethod
    @cached(LEXEME_CACHE)
    async def find(cls, sc: str):
        return await cls.select().where(Lexeme.zh_sc == sc)


class Dictionary(Table):
    id = Serial(primary_key=True)
    name = Varchar(required=True)


class Definition(Table):
    id = Serial(primary_key=True)
    text = Varchar(length=1000, required=True)
    category = Varchar(null=True, required=True)
    lexeme = ForeignKey(Lexeme)
    dictionary = ForeignKey(Dictionary)
