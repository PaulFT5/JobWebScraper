import time

from rapidfuzz import process, fuzz
from functools import lru_cache
from backend.matching.config import get_config
from backend.matching.esco.index import index_lookup_table
from backend.matching.match_result_object import MatchResult
from backend.matching.normalization import qualifier_remover
import re


def fuzzy_match(skill, table=None):
    config = get_config()
    threshold = config["grounding"]["fuzzy_threshold"]
    gap = config["grounding"]["gap_acceptance_min"]
    min_len = config["grounding"]["fuzzy_min_length"]

    if table is None:
        table = index_lookup_table()
        valid_keys = build_valid_keys(min_len)
    else:
        valid_keys = [k for k, v in table.items() if len(k) >= min_len]

    key = qualifier_remover(skill or "")
    not_found = MatchResult(status="not found", simplified_key=key, method="fuzzy")

    if not key or len(key) < min_len:
        return not_found

    cutoff = threshold - gap
    results = process.extract(
        key,
        valid_keys,
        scorer=fuzz.ratio,
        score_cutoff=cutoff,
        limit=5,
    )

    if not results:
        return not_found

    best_key, best_score, _ = results[0]
    if best_score < threshold:
        return not_found

    input_digits = re.findall(r"\d+", key)
    match_digits = re.findall(r"\d+", best_key)
    if input_digits != match_digits:
        return not_found

    best_uris = table[best_key]["uris"]

    rival_score = None
    for k, score, _ in results[1:]:
        if table[k]["uris"] != best_uris:
            rival_score = score
            break

    if rival_score is not None and (best_score - rival_score) < gap:
        return not_found


    if len(best_uris) == 1:
        (concept,) = best_uris
        return MatchResult(status="match", simplified_key=key, method="fuzzy",
                           concept=concept, label_kind=table[best_key]["kind"], score=best_score)
    else:
        return MatchResult(status="ambiguous", simplified_key=key, method="fuzzy",
                           candidates=tuple(sorted(best_uris)), label_kind=table[best_key]["kind"], score=best_score)


@lru_cache(maxsize=1)
def build_valid_keys(min_len):
    table = index_lookup_table()
    return [k for k, v in table.items() if len(k) >= min_len]


def tester():

    t0 = time.perf_counter()
    res1 = fuzzy_match("python")
    t1 = time.perf_counter() - t0
    print(res1)
    print(f"First call time: {t1 * 1000:.2f} ms")

    t0 = time.perf_counter()
    res2 = fuzzy_match("javascript")
    t2 = time.perf_counter() - t0
    print(res2)
    print(f"Second call time: {t2 * 1000:.2f} ms")

    t0 = time.perf_counter()
    res3 = fuzzy_match("iso 9001")
    t3 = time.perf_counter() - t0
    print(res3)
    print(f"Third call time: {t3 * 1000:.2f} ms")

#tester()