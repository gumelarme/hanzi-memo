from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy import Column, String, ForeignKey, Table, select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID


# email only for demo
class User(UUIDBase):
    email: Mapped[str] = mapped_column(String(length=32))
    user_dictionaries: Mapped[list["Dictionary"]] = relationship(back_populates="user", lazy="selectin")


class Dictionary(UUIDBase):
    name: Mapped[str]
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User | None] = relationship(back_populates="user_dictionaries", lazy="selectin")
    definitions: Mapped[list["Definition"]] = relationship(back_populates="dictionary", lazy="select")

    @classmethod
    async def add_ignore_exists(cls, session: AsyncSession, name: str, user: User | None = None) -> "Dictionary":
        is_exist = exists().where(cls.name == name).select()
        if not await session.scalar(is_exist):
            session.add(Dictionary(name=name, user=user))

        return await session.scalar(select(cls).where(cls.name == name))


# TODO: Add constraint at least one of lexeme or definition must be filled
lexeme_example = Table(
    "lexeme_example",
    UUIDBase.metadata,
    Column("lexeme_id", ForeignKey("lexeme.id"), nullable=True),
    Column("definition_id", ForeignKey("definition.id"), nullable=True),
    Column("example_id", ForeignKey("example.id")),
)

lexeme_definition = Table(
    "lexeme_definition",
    UUIDBase.metadata,
    Column("lexeme_id", ForeignKey("lexeme.id")),
    Column("definition_id", ForeignKey("definition.id")),
)


class Example(UUIDBase):
    zh: Mapped[str]
    pinyin: Mapped[str]
    translation: Mapped[str | None]


class Definition(UUIDBase):
    text: Mapped[str]
    category: Mapped[str | None]
    examples: Mapped[list[Example]] = relationship(secondary=lexeme_example)

    dictionary_id: Mapped[UUID] = mapped_column(ForeignKey("dictionary.id"))
    dictionary: Mapped[Dictionary] = relationship(back_populates="definitions")


# TODO: Add constraint at least one of zh_sc or zh_tc must be filled
class Lexeme(UUIDBase):
    zh_sc: Mapped[str | None]
    zh_tc: Mapped[str | None]
    pinyin: Mapped[str]

    definitions: Mapped[list[Definition]] = relationship(secondary=lexeme_definition)
    examples: Mapped[list[Example]] = relationship(secondary=lexeme_example)

