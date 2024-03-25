from dataclasses import dataclass, field

from litestar import Controller, get
from litestar.dto import DataclassDTO
from litestar.exceptions import NotFoundException

from lipotes.dictionary.tables import Definition, Lexeme


@dataclass
class LexemeOut:
    id: str
    zh_sc: str | None
    zh_tc: str | None
    pinyin: str | None


@dataclass
class LexemeWithDefinition(LexemeOut):
    definitions: list[dict[str, any]] = field(default_factory=list)


# TODO: fetch lexeme example end points
class LexemeController(Controller):
    path = "/lexemes"

    @get("/{lexeme_id:int}", return_dto=DataclassDTO[LexemeWithDefinition])
    async def get_lexeme_by_id(self, lexeme_id: int) -> LexemeWithDefinition:
        result = await Lexeme.select().where(Lexeme.id == lexeme_id).first()
        if result is None:
            raise NotFoundException()

        result = LexemeWithDefinition(**result)
        # noinspection PyTypeChecker
        definitions = await Definition.select(
            Definition.all_columns(exclude=[Definition.id, Definition.lexeme])
        ).where(Definition.lexeme == lexeme_id)
        if definitions is not None:
            result.definitions = definitions

        return result
