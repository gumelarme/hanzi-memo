import asyncio
import sys
from typing import Type

from dotenv import load_dotenv

from alfred.command import Command

from .migrate import MigrateCommand
from .seed_collection import SeedCollectionCommand
from .seed_dict import SeedDictCommand
from .seed_pleco import SeedPlecoCommand

commands: dict[str, Type[Command]] = {
    "migrate": MigrateCommand,
    "seed-dict": SeedDictCommand,
    "seed-coll": SeedCollectionCommand,
    "seed-pleco": SeedPlecoCommand,
}


async def main():
    cmd, *args = sys.argv[1:]

    is_help = False
    if cmd == "help":
        is_help = True
        cmd = args[0]

    if cmd not in commands:
        print(f"Command {cmd!r} not found")
        print("Available commands: ")
        print("\n".join([f"  - {x}" for x in commands]))
        return

    if is_help:
        print(commands[cmd].help(cmd))
        return

    await commands[cmd].run(args)


if __name__ == "__main__":
    load_dotenv()

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    if loop.is_running():
        loop.close()
