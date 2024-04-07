from async_lru import alru_cache
from piccolo.columns import ForeignKey, Serial, Varchar
from piccolo.table import Table


class Lexeme(Table):
    id = Serial(primary_key=True)
    zh_sc = Varchar(null=True, required=True)
    zh_tc = Varchar(null=True, required=True)
    pinyin = Varchar(null=True, required=True)

    @classmethod
    @alru_cache(maxsize=2**12)
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
