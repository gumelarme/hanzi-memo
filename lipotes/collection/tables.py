from piccolo.columns import ForeignKey, Serial, Varchar
from piccolo.table import Table

from lipotes.dictionary.tables import Lexeme


class Collection(Table):
    id = Serial(primary_key=True)
    name = Varchar()


class LexemeCollection(Table):
    collection = ForeignKey(Collection)
    lexeme = ForeignKey(Lexeme)
