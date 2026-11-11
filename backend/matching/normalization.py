import re

import unicodedata


def word_normalizer(word: str) -> str:
    word = unicodedata.normalize('NFKC', word)
    # Unicode hyphens/dashes (U+2010-U+2015, minus sign) -> ASCII '-'; NFKC maps the
    # non-breaking hyphen U+2011 only to U+2010, not to '-'.
    word = re.sub(r"[\u2010-\u2015\u2212]", "-", word)
    word = re.sub(r"['‘’`´]", "'", re.sub(r"[•·]", " ", word))
    word = re.sub(r"\s+", " ", word)
    chars_to_strip = " ,;:!?\"'“”‘’`*-"
    word = word.strip(chars_to_strip).rstrip(".")
    word = word.strip(chars_to_strip)

    return word.casefold()

# Java (programming language) -> Java || e-commerce -> e commerce
def qualifier_remover(word: str) -> str:
    word = re.sub(r"\s*-\s*", " ", word_normalizer(word)).strip()
    word = re.sub(r"\s*\([^)]*\)\s*$", "", word_normalizer(word)).strip()
    return word_normalizer(word).casefold()


