import asyncio
import sys
from typing import Callable

from dotenv import load_dotenv
from app.db.seed import migrate_schema, seed_dict
from app.db.connection import get_engine


def migrate(args: list[str]):
    drop = len(args) == 1 and args[0] == "drop"
    asyncio.run(migrate_schema(get_engine(), drop))


commands: dict[str, Callable] = {
    "migrate": migrate,
    "populate": lambda args: asyncio.run(seed_dict(args)),
}


def main():
    cmd, *args = sys.argv[1:]
    if cmd not in commands:
        print(f"Command {cmd!r} not found")
        return

    commands[cmd](args)


if __name__ == "__main__":
    load_dotenv()
    main()
