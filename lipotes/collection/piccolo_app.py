import os

from piccolo.conf.apps import AppConfig, Command, table_finder

from lipotes.collection.command.seed import seed

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


APP_CONFIG = AppConfig(
    app_name="collection",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),
    table_classes=table_finder(
        modules=["lipotes.collection.tables"], exclude_imported=True
    ),
    migration_dependencies=[],
    commands=[Command(seed)],
)
