from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    String,
    Table,
    UniqueConstraint,
    exists,
    or_,
    select,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column, relationship


# email only for demo
class User(UUIDBase):
    email: Mapped[str] = mapped_column(String(length=32))
    dictionaries: Mapped[list["Dictionary"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    collections: Mapped[list["Collection"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    lexeme_blacklist: Mapped[list["LexemeBlacklist"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    collection_blacklist: Mapped[list["CollectionBlacklist"]] = relationship(
        back_populates="user", lazy="selectin"
    )


class Dictionary(UUIDBase):
    name: Mapped[str]
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User | None] = relationship(
        back_populates="dictionaries", lazy="selectin"
    )
    definitions: Mapped[list["Definition"]] = relationship(
        back_populates="dictionary", lazy="noload"
    )

    @classmethod
    async def add_ignore_exists(
        cls, session: AsyncSession, name: str, user: User | None = None
    ) -> "Dictionary":
        is_exist = exists().where(cls.name == name).select()
        if not await session.scalar(is_exist):
            session.add(Dictionary(name=name, user=user))

        return await session.scalar(select(cls).where(cls.name == name))


lexeme_example = Table(
    "lexeme_example",
    UUIDBase.metadata,
    Column("lexeme_id", ForeignKey("lexeme.id"), nullable=True),
    Column("example_id", ForeignKey("example.id")),
)

definition_example = Table(
    "definition_example",
    UUIDBase.metadata,
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
    examples: Mapped[list[Example]] = relationship(secondary=definition_example)

    dictionary_id: Mapped[UUID] = mapped_column(ForeignKey("dictionary.id"))
    dictionary: Mapped[Dictionary] = relationship(
        back_populates="definitions", lazy="select"
    )


lexeme_collection = Table(
    "lexeme_collection",
    UUIDBase.metadata,
    Column("lexeme_id", ForeignKey("lexeme.id")),
    Column("collection_id", ForeignKey("collection.id")),
    UniqueConstraint("lexeme_id", "collection_id"),
    Index("lexeme_id", "collection_id"),
)


# TODO: Set Collation
# TODO: Add constraint at least one of zh_sc or zh_tc must be filled
class Lexeme(UUIDBase):
    zh_sc: Mapped[str | None]
    zh_tc: Mapped[str | None]
    pinyin: Mapped[str | None]

    definitions: Mapped[list[Definition]] = relationship(
        secondary=lexeme_definition,
        lazy="selectin",
    )
    examples: Mapped[list[Example]] = relationship(
        secondary=lexeme_example, lazy="selectin"
    )
    collections: Mapped[list["Collection"]] = relationship(
        secondary=lexeme_collection, lazy="noload", back_populates="lexemes"
    )

    __table_args__ = (
        UniqueConstraint("zh_sc", "zh_tc", "pinyin", name="zh_pinyin_combo"),
        Index("zh_index", "zh_sc", "zh_tc"),
    )

    @classmethod
    async def find(
        cls, session: AsyncSession, sc: str, tc: str | None = None
    ) -> list["Lexeme"]:
        if not tc:
            tc = sc

        query = (
            select(cls)
            .where(or_(cls.zh_sc == sc, cls.zh_tc == tc))
            .order_by(cls.pinyin)
        )
        return list((await session.scalars(query)).all())


class Collection(UUIDBase):
    name: Mapped[str]
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User | None] = relationship(
        back_populates="collections", lazy="selectin"
    )

    lexemes: Mapped[list[Lexeme]] = relationship(
        lazy="noload",
        secondary=lexeme_collection,
        back_populates="collections",
    )


@declarative_mixin
class Blacklist:
    is_active: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))


class LexemeBlacklist(Blacklist, UUIDBase):
    user: Mapped[User] = relationship(
        back_populates="lexeme_blacklist", lazy="selectin"
    )
    lexeme_id: Mapped[UUID] = mapped_column(ForeignKey("lexeme.id"))
    lexeme: Mapped[Lexeme] = relationship(lazy="noload")


class CollectionBlacklist(Blacklist, UUIDBase):
    user: Mapped[User] = relationship(
        back_populates="collection_blacklist", lazy="selectin"
    )
    collection_id: Mapped[UUID] = mapped_column(ForeignKey("collection.id"))
    collection: Mapped[Collection] = relationship(lazy="noload")


preset_collection = Table(
    "preset_collection",
    UUIDBase.metadata,
    Column("preset_id", ForeignKey("preset.id")),
    Column("collection_id", ForeignKey("collection.id")),
)

preset_lexeme = Table(
    "preset_lexeme",
    UUIDBase.metadata,
    Column("preset_id", ForeignKey("preset.id")),
    Column("lexeme_id", ForeignKey("lexeme.id")),
)


class Text(UUIDBase):
    title: Mapped[str] = mapped_column(default="")
    text: Mapped[str] = mapped_column(default="")


class Preset(UUIDBase):
    friendly_name: Mapped[str] = mapped_column()  # TODO: use hashids
    text_id: Mapped[UUID] = mapped_column(ForeignKey("text.id"))
    text: Mapped[Text] = relationship(lazy="select")

    lexemes: Mapped[list[Lexeme]] = relationship(secondary=preset_lexeme)
    collections: Mapped[list[Collection]] = relationship(secondary=preset_collection)
