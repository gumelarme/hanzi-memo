from piccolo.columns import ForeignKey, Serial, Varchar
from piccolo.table import Table


class Lexeme(Table):
    id = Serial(primary_key=True)
    zh_sc = Varchar(null=True)
    zh_tc = Varchar(null=True)
    pinyin = Varchar(null=True)


class Dictionary(Table):
    id = Serial(primary_key=True)
    name = Varchar()


class Definition(Table):
    id = Serial(primary_key=True)
    text = Varchar(length=1000)
    category = Varchar(null=True)
    lexeme = ForeignKey(Lexeme)
    dictionary = ForeignKey(Dictionary)
