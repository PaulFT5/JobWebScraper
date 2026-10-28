"""ESCO index: exact match (step A) and fuzzy match (step B).

Synthetic tables (built with the index's own add_label) test the rules in isolation;
a few checks run against the real ESCO index. Nothing is written anywhere.
Fuzzy is expected as fuzzy_match(skill, table=None) -> MatchResult in esco/index.py;
until it exists every F check shows FAIL.
Scores quoted below are rapidfuzz fuzz.ratio values (measured 2026-10-27).
"""
import time
from common import summary, check
from backend.matching.esco import index
from backend.matching.esco.index import add_label, exact_match, index_lookup_table

fuzzy = getattr(index, "fuzzy_match", None)


def table(*labels):
    """labels: (label, uri, kind); keys simplified the same way the real index does."""
    t = {}
    for label, uri, kind in labels:
        add_label(t, index.qualifier_remover(label), uri, kind)
    return t


def run_fuzzy(id_, name, t, skill, expect):
    if fuzzy is None:
        check(id_, name, False, "fuzzy_match not implemented in esco/index.py")
        return
    try:
        r = fuzzy(skill, table=t)
    except Exception as e:
        check(id_, name, False, f"{skill!r} raised {type(e).__name__}: {e}")
        return
    ok, why = expect(r)
    check(id_, name, ok, f"{skill!r} -> status={r.status}, concept={r.concept}, candidates={r.candidates}, "
                         f"score={r.score}, method={r.method}; {why}")


# ---------- E: exact, synthetic
T = table(("Java (computer programming)", "JAVA", "preferred"), ("JavaScript", "JS", "preferred"),
          ("e-commerce", "ECOM", "preferred"),
          ("cloud computing", "CLOUD_A", "preferred"), ("cloud computing", "CLOUD_B", "alt"),
          ("data mining", "MINE_A", "alt"), ("data mining", "MINE_B", "alt"))

r = exact_match("Java", T)
check("E1", "plain label matches", r.status == "match" and r.concept == "JAVA" and r.label_kind == "preferred", str(r))
r = exact_match("Java (programming language)", T)
check("E2", "trailing qualifier removed", r.status == "match" and r.concept == "JAVA", str(r))
r = exact_match("E-Commerce", T)
check("E3", "hyphen/case simplified", r.status == "match" and r.concept == "ECOM", str(r))
r = exact_match("Java", T)
check("E4", "Java != JavaScript", r.concept != "JS", str(r))
r = exact_match("cloud computing", T)
check("E5", "better label kind wins", r.status == "match" and r.concept == "CLOUD_A", str(r))
r = exact_match("data mining", T)
check("E6", "same-kind tie stays ambiguous", r.status == "ambiguous" and r.candidates == ("MINE_A", "MINE_B"), str(r))
check("E7", "empty / blank -> not found",
      all(exact_match(s, T).status == "not found" for s in ("", "   ", None)), "'', '   ', None")
r = exact_match("Kotlin", T)
check("E8", "unknown -> not found + key", r.status == "not found" and r.simplified_key == "kotlin", str(r))

# ---------- E: exact, real ESCO index
REAL = index_lookup_table()
js, java = exact_match("JavaScript"), exact_match("Java")
check("ER1", "real: JavaScript matches", js.status == "match", str(js))
check("ER2", "real: Java != JavaScript", java.status == "match" and java.concept != js.concept, f"{java.concept} vs {js.concept}")
check("ER3", "real: index built", len(REAL) > 50000, f"{len(REAL)} keys")

# ---------- F: fuzzy, synthetic
TJ = table(("JavaScript", "JS", "preferred"), ("java script", "JS", "alt"))
run_fuzzy("F1", "typo matches (94.7)", TJ, "javscript",
          lambda r: (r.status == "match" and r.concept == "JS" and r.method == "fuzzy", "expected match JS, method fuzzy"))
run_fuzzy("F2", "score reported", TJ, "javscript",
          lambda r: (r.score is not None and r.score >= 90, "expected score >= 90"))
run_fuzzy("F3", "2 labels of 1 concept not ambiguous (94.7 / 90.0)", TJ, "javscript",
          lambda r: (r.status == "match", "gap between labels of the same concept must not count"))
run_fuzzy("F4", "Java != JavaScript (57.1)", TJ, "java",
          lambda r: (r.status == "not found", "whole-string scorer, no partial match"))

TS = table(("R", "R", "preferred"), ("Go", "GO", "preferred"), ("C", "C", "preferred"))
for i, s in enumerate(("R", "Go", "C"), 1):
    run_fuzzy(f"F5.{i}", f"short '{s}' exact only", TS, s,
              lambda r: (r.status == "not found", "below min length 4: no fuzzy even at score 100"))

TN = table(("ISO 14001 environmental management", "ISO14001", "preferred"))
run_fuzzy("F6.1", "ISO 9001 != 14001 (95.5)", TN, "ISO 9001 environmental management",
          lambda r: (r.status == "not found", "numbers must match exactly"))
run_fuzzy("F6.2", "ISO 14002 != 14001 (97.1)", TN, "ISO 14002 environmental management",
          lambda r: (r.status == "not found", "numbers must match exactly"))
run_fuzzy("F6.3", "same numbers still fuzzy", TN, "ISO 14001 enviromental management",
          lambda r: (r.status == "match" and r.concept == "ISO14001", "typo with equal numbers"))

TD = table(("data analysis", "ANALYSIS", "preferred"), ("data analytics", "ANALYTICS", "preferred"))
run_fuzzy("F7", "clear winner (92.3 vs 81.5)", TD, "data analysys",
          lambda r: (r.status == "match" and r.concept == "ANALYSIS", "gap 10.8 >= 5"))
run_fuzzy("F8", "runner-up below 90 but within gap (92.3 vs 88.0)", TD, "data analyti",
          lambda r: (r.status == "ambiguous" and set(r.candidates) == {"ANALYSIS", "ANALYTICS"}, "gap 4.3 < 5"))

TT = table(("data analysis", "ANALYSIS", "preferred"), ("data analyses", "ANALYSES", "preferred"))
run_fuzzy("F9", "two concepts tied (92.3 / 92.3)", TT, "data analysxs",
          lambda r: (r.status == "ambiguous" and set(r.candidates) == {"ANALYSIS", "ANALYSES"}, "gap 0"))

TC = table(("cloud computing", "CLOUD_A", "preferred"), ("cloud computing", "CLOUD_B", "preferred"))
run_fuzzy("F10", "best key has 2 concepts (96.6)", TC, "cloud computng",
          lambda r: (r.status == "ambiguous" and set(r.candidates) == {"CLOUD_A", "CLOUD_B"}, "ambiguous key"))

TP = table(("project management", "PM", "preferred"))
run_fuzzy("F11", "below threshold (35.3)", TP, "machine learning",
          lambda r: (r.status == "not found", "score < 90"))
run_fuzzy("F12", "empty / blank", TP, "   ",
          lambda r: (r.status == "not found", "no scoring on empty input"))
run_fuzzy("F13", "simplified key kept", TP, "Project-Managment",
          lambda r: (r.status == "match" and r.simplified_key == "project managment", "hyphen simplified first"))

# ---------- F: fuzzy, real ESCO index
run_fuzzy("FR1", "real: javscript -> JavaScript", None, "javscript",
          lambda r: (r.status == "match" and r.concept == js.concept, f"expected {js.concept}"))
pm = exact_match("project management")
run_fuzzy("FR2", "real: project managment", None, "project managment",
          lambda r: (r.status == "match" and r.concept == pm.concept, f"expected {pm.concept}"))
iso = exact_match("ISO 14001")
run_fuzzy("FR3", "real: ISO 14002 not ISO 14001", None, "ISO 14002",
          lambda r: (r.concept != iso.concept and iso.concept not in r.candidates, f"must not be {iso.concept}"))
run_fuzzy("FR4", "real: Java not JavaScript", None, "java",
          lambda r: (r.concept != js.concept and js.concept not in r.candidates, "no partial match"))
if fuzzy is not None:
    skills = ["javscript", "project managment", "machine lerning", "custmer service", "kubernets"]
    fuzzy(skills[0])  # warm-up builds the cached key list
    t0 = time.perf_counter()
    for s in skills:
        fuzzy(s)
    ms = (time.perf_counter() - t0) * 1000 / len(skills)
    check("FR5", "real: speed per lookup (info)", True, f"{ms:.1f} ms avg over {len(skills)} lookups, {len(REAL)} keys")

raise SystemExit(summary())
