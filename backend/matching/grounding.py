from rapidfuzz import process, fuzz
from backend.matching.config import get_config
from backend.matching.esco.index import index_lookup_table

def grounding(skill, table=None, min_length=4, score_cutoff=80.0):
    config = get_config()

    threshold = config["grounding"]["fuzzy_threshold"]
    gap = config["grounding"]["gap_acceptance_min"]
    min_len = config["grounding"]["fuzzy_min_length"]

    if table is None:
        table = index_lookup_table()

    valid_keys = [k for k in table.keys() if len(k) >= min_len]

    score = process.extract(skill, valid_keys, scorer=fuzz.ratio, score_cutoff= threshold - gap, limit=5)

    return None