from functools import lru_cache
from backend.matching.esco.loader import load_all_csv
from backend.matching.match_result_object import MatchResult
from backend.matching.normalization import word_normalizer, qualifier_remover

LABEL_RANK = {"preferred": 0, "alt": 1, "hidden": 2}

def add_label(table, key, uri, kind):
    entry = table.get(key)
    if entry is None or LABEL_RANK[kind] < LABEL_RANK[entry["kind"]]:
        table[key] = {"kind": kind, "uris": {uri}}
    elif kind == entry["kind"]:
        entry["uris"].add(uri)

@lru_cache(maxsize=1)
def index_lookup_table():
    hierarchy, skills, skill_pillars = load_all_csv()
    table = dict()

    for uri, entry in skills.items():
        labels = [("preferred", entry["preferredLabel"])]
        labels += [("alt", label) for label in entry["altLabels"]]
        labels += [("hidden", label) for label in entry["hiddenLabels"]]

        for kind, label in labels:
            key = qualifier_remover(label or "")
            if key:
                add_label(table, key, uri, kind)
    return table


def exact_match(skill, table=None):
    if table is None:
        table = index_lookup_table()

    if not skill or not skill.strip():
        return MatchResult(status="not found")

    key = qualifier_remover(skill)
    if not key:
        return MatchResult(status="not found")

    entry = table.get(key)

    if entry is None:
        return MatchResult(status="not found", simplified_key=key)

    uris = entry["uris"]
    kind = entry["kind"]

    if len(uris) == 1:
        (concept,) = uris
        return MatchResult(
            status="match",
            concept=concept,
            label_kind=kind,
            simplified_key=key,
        )

    return MatchResult(
        status="ambiguous",
        candidates=tuple(sorted(uris)),
        label_kind=kind,
        simplified_key=key,
    )


