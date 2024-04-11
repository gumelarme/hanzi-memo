import redis


class LexemeCache:
    def __init__(self, connection_pool: redis.ConnectionPool):
        self.r = redis.Redis(connection_pool=connection_pool)
        self.KEY_LEXEME = "lexeme"
        self.KEY_UNAVAILABLE_LEXEME = "unavailable_lexeme"

    @classmethod
    def zh_prefix(cls, is_simplified=True) -> str:
        return "zh_sc" if is_simplified else "zh_tc"

    def cache_lexemes(
        self,
        char: str,
        lexemes: list[dict[str, str]],
        is_sc=True,
    ) -> None:
        sc_key = f"{self.zh_prefix(is_sc)}:{char}"
        if not lexemes:
            self.r.sadd(sc_key, 0)
            return

        with self.r.pipeline() as pipe:
            for lex in lexemes:
                lex_id = lex["id"]
                pipe.sadd(sc_key, lex_id)
                pipe.hset(
                    f"{self.KEY_LEXEME}:{lex_id}",
                    mapping={k: v for k, v in lex.items() if k != "id"},
                )
            pipe.execute()

    def get_lexemes(self, char: str, is_sc=True) -> list[dict]:
        members = self.r.smembers(f"{self.zh_prefix(is_sc)}:{char}")
        return [self.get_lexemes_by_id(lex_id) for lex_id in members]

    def get_lexemes_by_id(self, lex_id: int) -> dict[str, str]:
        data = self.r.hgetall(f"{self.KEY_LEXEME}:{lex_id}")
        if not data:
            return data

        data["id"] = lex_id
        return data

    def is_lexeme_unavailable(self, char: str, is_sc=True) -> bool:
        key = f"{self.KEY_UNAVAILABLE_LEXEME}:{self.zh_prefix(is_sc)}"
        return bool(self.r.sismember(key, char))

    def set_lexeme_unavailable(self, char: str, is_sc=True) -> None:
        self.r.sadd(f"{self.KEY_UNAVAILABLE_LEXEME}:{self.zh_prefix(is_sc)}", char)
