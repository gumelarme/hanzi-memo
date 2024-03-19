from piccolo.columns import Serial, Varchar
from piccolo.table import Table


class Lexeme(Table):
    id = Serial(primary_key=True)
    zh_sc = Varchar(null=True)
    zh_tc = Varchar(null=True)
    pinyin = Varchar(null=True)
