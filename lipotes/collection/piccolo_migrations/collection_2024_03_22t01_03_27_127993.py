from piccolo.apps.migrations.auto.migration_manager import MigrationManager

from lipotes.collection.tables import LexemeCollection

ID = "2024-03-22T01:03:27:127993"
VERSION = "1.4.2"
DESCRIPTION = "Add unique constraint to (collection, lexeme) columns"


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)

    # NOTE: Composite unique constraint are still unresolved issue
    # https://github.com/piccolo-orm/piccolo/issues/172

    async def add_unique_constraint():
        await LexemeCollection.raw(
            """
            ALTER TABLE lexeme_collection
            ADD CONSTRAINT lexeme_collection_UQ
            UNIQUE (collection_id, lexeme_id);
            """
        )

    manager.add_raw(add_unique_constraint)
    return manager
