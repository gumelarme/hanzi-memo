from piccolo.apps.migrations.auto.migration_manager import MigrationManager

from lipotes.util.migration import make_table

ID = "2024-03-23T15:56:01:879943"
VERSION = "1.4.2"
DESCRIPTION = "Init text table"


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)
    table = make_table("Text", "text", manager)
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
        column_name="title",
        column_class_name="Varchar",
        params={
            "null": False,
        }
    )

    manager.add_column(
        **table,
        column_name="text",
        column_class_name="Varchar",
        params={
            "null": False,
            "length": 3000,
            "default": "",
        }
    )

    return manager
