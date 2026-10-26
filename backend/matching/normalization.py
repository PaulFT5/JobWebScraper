import re

import unicodedata


def word_normalizer(word: str) -> str:
    word = unicodedata.normalize('NFKC', word)
    word = re.sub(r"['‘’`´]", "'", re.sub(r"[•*·]", " ", word))
    word = re.sub(r"\s+", " ", word)
    return word.strip(" .,;:-!?\"'“”‘’`").casefold()
