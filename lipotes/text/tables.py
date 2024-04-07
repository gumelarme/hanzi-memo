from piccolo.columns import Serial, Varchar
from piccolo.table import Table


class Text(Table):
    id = Serial(primary_key=True)
    title = Varchar(null=False, required=True)
    text = Varchar(length=3000, default="", required=True)
