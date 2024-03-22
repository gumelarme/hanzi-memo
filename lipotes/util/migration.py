from piccolo.apps.migrations.auto import MigrationManager


def make_table(
    class_name: str, table_name: str, manager: MigrationManager
) -> dict[str, str]:
    table = dict(
        table_class_name=class_name,
        tablename=table_name,
    )

    manager.add_table(class_name, table_name)
    return table
