from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.query.methods.alter import AddColumn

ID = "2024-03-19T13:24:42:743277"
VERSION = "1.4.2"
DESCRIPTION = "Init: table creation"


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)
    class_name = "Lexeme"
    table_name = "lexeme"

    table = dict(
        table_class_name=class_name,
        tablename=table_name,
    )
    manager.add_table(class_name, tablename=table_name)
    manager.add_column(
        **table,
        column_name="id",
        column_class_name="Serial",
        params={
            "null": False,
            "primary_key": True,
        }
    )

    manager.add_column(
        **table,
        column_name="zh_sc",
        column_class_name="Varchar",
        params={
            "null": True,
        }
    )

    manager.add_column(
        **table,
        column_name="zh_tc",
        column_class_name="Varchar",
        params={
            "null": True,
        }
    )

    manager.add_column(
        **table,
        column_name="pinyin",
        column_class_name="Varchar",
        params={
            "null": True,
        }
    )

    return manager
