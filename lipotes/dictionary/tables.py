from asyncache import cached
from cachetools import LRUCache
from piccolo.columns import ForeignKey, Serial, Varchar
from piccolo.table import Table

from lipotes.redis import pool

from .cache import LexemeCache

LEXEME_CACHE_BY_SC = LRUCache(maxsize=2**14)


def get_redis_lexeme_by_sc(cache: LexemeCache, sc: str) -> tuple[bool, list[dict]]:
    if cache.is_lexeme_unavailable(sc):
        return True, []

    if lexeme := cache.get_lexemes(sc):
        return True, lexeme

    return False, []


class Lexeme(Table):
    id = Serial(primary_key=True)
    zh_sc = Varchar(null=True, required=True)
    zh_tc = Varchar(null=True, required=True)
    pinyin = Varchar(null=True, required=True)

    @classmethod
    @cached(LEXEME_CACHE_BY_SC)
    async def find(cls, sc: str) -> list[dict]:
        cache = LexemeCache(pool)
        is_found, lexeme = get_redis_lexeme_by_sc(cache, sc)
        if is_found:
            return lexeme

        lexemes = await cls.select().where(Lexeme.zh_sc == sc)
        if not lexemes:
            cache.set_lexeme_unavailable(sc)
            return []

        cache.cache_lexemes(sc, lexemes)
        return lexemes


class Dictionary(Table):
    id = Serial(primary_key=True)
    name = Varchar(required=True)


class Definition(Table):
    id = Serial(primary_key=True)
    text = Varchar(length=1000, required=True)
    category = Varchar(null=True, required=True)
    lexeme = ForeignKey(Lexeme)
    dictionary = ForeignKey(Dictionary)
