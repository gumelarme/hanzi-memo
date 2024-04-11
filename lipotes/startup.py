import structlog
from cachetools.keys import hashkey

from lipotes.collection.tables import LexemeCollection
from lipotes.dictionary.tables import LEXEME_CACHE_BY_SC, Lexeme
from lipotes.dictionary.text_processor.tokenizer import init_tokenizer


async def precache_lexemes():
    logger = structlog.get_logger()
    logger.info("Precaching...")
    # TODO: Limit to only cache default collections
    # TODO: Add frequent hit lexeme to cache
    lex_ids = (
        LexemeCollection.select(LexemeCollection.lexeme).output(as_list=True).run_sync()
    )

    lexemes = Lexeme.select().where(Lexeme.id.is_in(lex_ids)).run_sync()

    for lex in lexemes:
        # FIXME: risky, better implement custom lru cache with precaching mechanism
        key = hashkey(Lexeme, lex["zh_sc"])
        try:
            LEXEME_CACHE_BY_SC[key].append(lex)
        except KeyError:
            LEXEME_CACHE_BY_SC[key] = [lex]

    logger.info("Precaching done", cache_size=LEXEME_CACHE_BY_SC.currsize)


startup_functions = [
    init_tokenizer,
    precache_lexemes,
]
