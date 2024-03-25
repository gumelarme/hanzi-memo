import structlog
from jieba import Tokenizer

log = structlog.get_logger()
tokenizer = Tokenizer()


def init_tokenizer():
    # TODO: add jieba big user dict
    # TODO: add misses word to the tokenizer
    # TODO: add user collection word to tokenizer

    i_am_lipotes = tokenizer.lcut("我是白暨豚")
    log.info("Initializing jieba tokenizer", cuts=i_am_lipotes)
