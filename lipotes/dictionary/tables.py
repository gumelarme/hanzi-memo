import structlog
from asyncache import cached
from cachetools import LRUCache
from cachetools.keys import methodkey
from piccolo.columns import ForeignKey, Serial, Varchar
from piccolo.table import Table

from lipotes.redis import pool

from .cache import LexemeCache

LEXEME_CACHE_BY_SC = LRUCache(maxsize=2**14)
LEXEME_CACHE_BY_ID = LRUCache(maxsize=2**14)


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
    @cached(LEXEME_CACHE_BY_SC, key=methodkey)
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

    @classmethod
    async def find_by_id(cls, id_: int) -> dict:
        result = await cls.find_multiple_by_id([id_])
        return result[0] or {}

    @classmethod
    async def find_multiple_by_id(cls, ids: list[int]) -> list[dict]:
        cache = LexemeCache(pool)

        @cached(LEXEME_CACHE_BY_ID)
        def find_cached_by_id(lex_id: int) -> dict:
            return cache.get_lexemes_by_id(lex_id)

        not_found = []
        lexemes = []
        for id_ in ids:
            lex = find_cached_by_id(id_)
            if not lex:
                not_found.append(id_)
                continue
            lexemes.append(lex)

        if not_found:
            not_found_lexeme = await Lexeme.select().where(Lexeme.id.is_in(not_found))
            for lex in not_found_lexeme:
                cache.cache_lexemes(lex["zh_sc"], [lex])
            lexemes.extend(not_found_lexeme)
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
