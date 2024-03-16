import asyncio
import sys
from typing import Callable

from dotenv import load_dotenv

from app.db.connection import get_engine
from app.db.seed import (
    migrate_schema,
    seed_collection,
    seed_dict,
    seed_pleco,
    seed_text,
)


async def migrate(args: list[str]):
    drop = len(args) == 1 and args[0] == "drop"
    await migrate_schema(get_engine(), drop)


commands: dict[str, Callable] = {
    "migrate": migrate,
    "seed_dict": seed_dict,
    "seed_coll": seed_collection,
    "seed_text": seed_text,
    "seed_pleco": seed_pleco,
}

seeding_func = Callable[[str, int, int | None], None]


async def main():
    cmd, *args = sys.argv[1:]
    if cmd not in commands:
        print(f"Command {cmd!r} not found")
        return

    await commands[cmd](args)


if __name__ == "__main__":
    load_dotenv()

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    if loop.is_running():
        loop.close()
