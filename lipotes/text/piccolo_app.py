import os

from piccolo.conf.apps import AppConfig, Command, table_finder

from lipotes.text.command.seed import seed_text

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


APP_CONFIG = AppConfig(
    app_name="text",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),
    table_classes=table_finder(modules=["lipotes.text.tables"], exclude_imported=True),
    migration_dependencies=[],
    commands=[Command(seed_text, aliases=["seed"])],
)
