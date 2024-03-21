from piccolo.apps.migrations.auto.migration_manager import MigrationManager

from lipotes.collection.tables import LexemeCollection

ID = "2024-03-22T01:03:27:127993"
VERSION = "1.4.2"
DESCRIPTION = "Add unique constraint to (collection, lexeme) columns"


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)

    # NOTE: Composite unique constraint are still unresolved issue
    # https://github.com/piccolo-orm/piccolo/issues/172

    table_name = "lexeme_collection"
    constraint_name = f"{table_name}_uq"

    async def add_unique_constraint():
        await LexemeCollection.raw(
            f"""
            ALTER TABLE {table_name}
            ADD CONSTRAINT {constraint_name}
            UNIQUE (collection_id, lexeme_id);
            """
        )

    async def drop_unique_constraint():
        await LexemeCollection.raw(
            f"""
            ALTER TABLE {table_name}
            DROP CONSTRAINT {constraint_name};
            """
        )

    manager.add_raw(add_unique_constraint)
    manager.add_raw_backwards(drop_unique_constraint)

    return manager
