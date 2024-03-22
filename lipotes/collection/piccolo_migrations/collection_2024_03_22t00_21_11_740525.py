from piccolo.apps.migrations.auto.migration_manager import MigrationManager

from lipotes.util.migration import make_table

ID = "2024-03-22T00:21:11:740525"
VERSION = "1.4.2"
DESCRIPTION = "Init: create collections and lexeme_collection table"


def create_collection_table(manager: MigrationManager):
    table = make_table("Collection", "collection", manager)
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


def create_lexeme_collection_table(manager: MigrationManager):
    table = make_table("LexemeCollection", "lexeme_collection", manager)
    manager.add_column(
        **table,
        column_name="collection",
        db_column_name="collection",
        column_class_name="ForeignKey",
        params={
            "references": "collection",
            "null": False,
        }
    )

    manager.add_column(
        **table,
        column_name="lexeme",
        db_column_name="lexeme",
        column_class_name="ForeignKey",
        params={
            "references": "lexeme",
            "null": False,
        }
    )


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)

    create_collection_table(manager)
    create_lexeme_collection_table(manager)

    return manager
