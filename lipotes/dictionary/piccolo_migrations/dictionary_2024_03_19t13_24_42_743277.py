from piccolo.apps.migrations.auto.migration_manager import MigrationManager

ID = "2024-03-19T13:24:42:743277"
VERSION = "1.4.2"
DESCRIPTION = "Init: table creation"


def create_lexeme_table(manager: MigrationManager):
    table = dict(
        table_class_name="Lexeme",
        tablename="lexeme",
    )
    manager.add_table(table["table_class_name"], tablename=table["tablename"])
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


def create_dictionary_table(manager: MigrationManager):
    table = dict(
        table_class_name="Dictionary",
        tablename="dictionary",
    )

    manager.add_table(table["table_class_name"], tablename=table["tablename"])
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
        column_name="name",
        column_class_name="Varchar",
        params={
            "null": False,
        }
    )


def create_definition_table(manager: MigrationManager):
    table = dict(
        table_class_name="Definition",
        tablename="definition",
    )

    manager.add_table(table["table_class_name"], tablename=table["tablename"])
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
        column_name="text",
        column_class_name="Varchar",
        params={
            "null": False,
            "length": 1000,
        }
    )

    manager.add_column(
        **table,
        column_name="category",
        column_class_name="Varchar",
        params={
            "null": True,
        }
    )

    manager.add_column(
        **table,
        column_name="lexeme",
        db_column_name="lexeme",
        column_class_name="ForeignKey",
        params={
            "references": "lexeme",
            "null": True,
        }
    )

    manager.add_column(
        **table,
        column_name="dictionary",
        db_column_name="dictionary",
        column_class_name="ForeignKey",
        params={
            "references": "dictionary",
            "null": True,
        }
    )


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)
    create_lexeme_table(manager)
    create_dictionary_table(manager)
    create_definition_table(manager)
    return manager
