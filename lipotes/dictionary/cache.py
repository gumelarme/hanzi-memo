import redis


class LexemeCache:
    def __init__(self, connection_pool: redis.ConnectionPool):
        self.r = redis.Redis(connection_pool=connection_pool)
        self.KEY_LEXEME = "lexeme"
        self.KEY_UNAVAILABLE_LEXEME = "unavailable_lexeme"

    def cache_lexemes(
        self, char: str, lexemes: list[dict[str, str]], prefix="zh_sc"
    ) -> None:
        sc_key = f"{prefix}:{char}"
        if not lexemes:
            self.r.sadd(sc_key, 0)
            return

        for lex in lexemes:
            lex_id = lex["id"]
            self.r.sadd(sc_key, lex_id)
            self.r.hset(
                f"{self.KEY_LEXEME}:{lex_id}",
                mapping={k: v for k, v in lex.items() if k != "id"},
            )

    def get_lexemes(self, char: str, prefix="zh_sc") -> list[dict]:
        result = []
        for member in self.r.smembers(f"{prefix}:{char}"):
            data = self.r.hgetall(f"{self.KEY_LEXEME}:{member}")
            data["id"] = member
            result.append(data)
        return result

    def is_lexeme_unavailable(self, char: str, prefix="zh_sc") -> bool:
        key = f"{self.KEY_UNAVAILABLE_LEXEME}:{prefix}"
        return bool(self.r.sismember(key, char))

    def set_lexeme_unavailable(self, char: str, prefix="zh_sc") -> None:
        self.r.sadd(f"{self.KEY_UNAVAILABLE_LEXEME}:{prefix}", char)
