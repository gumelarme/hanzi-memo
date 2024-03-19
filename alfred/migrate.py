from advanced_alchemy.base import UUIDBase

from lipotes.db.connection import get_engine

from .command import Command


class MigrateCommand(Command):
    @classmethod
    async def run(cls, args: list[str]):
        drop = len(args) == 1 and args[0] == "drop"
        func = UUIDBase.metadata.drop_all if drop else UUIDBase.metadata.create_all
        engine = get_engine()

        async with engine.begin() as conn:
            await conn.run_sync(func)

    @classmethod
    def help(cls, command=None):
        return "\n".join(["Commands:", f"  - {command} [drop]"])
