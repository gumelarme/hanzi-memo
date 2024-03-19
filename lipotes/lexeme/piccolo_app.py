"""
Import all of the Tables subclasses in your app here, and register them with
the APP_CONFIG.
"""

import os

from piccolo.conf.apps import AppConfig, Command, table_finder

from lipotes.lexeme.command.dict import list_dict
from lipotes.lexeme.command.seed import seed

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


APP_CONFIG = AppConfig(
    app_name="lexeme",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),
    table_classes=table_finder(
        modules=["lipotes.lexeme.tables"], exclude_imported=True
    ),
    migration_dependencies=[],
    commands=[Command(list_dict, aliases=["help"]), Command(seed, aliases=["seed"])],
)
