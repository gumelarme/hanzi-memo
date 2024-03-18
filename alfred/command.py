from abc import ABC, abstractmethod


class Command(ABC):
    @classmethod
    @abstractmethod
    async def run(cls, args: list[str]):
        raise NotImplementedError

    @classmethod
    def help(cls, command=None) -> str:
        return "Help needed"
