"""CV side: parser dict -> skill names, tiers and grounded entries (matrix columns)."""
from dataclasses import asdict

from backend.matching.grounding import ground


def flatten_cv_skills(cv):
    """{"hard_skills": {tier: [skill, ...]}} -> [(skill, tier), ...]."""
    return [(skill, tier) for tier, skills in cv["hard_skills"].items() for skill in skills]


def ground_cv(cv):
    """Parser dict -> (names, tiers, grounded entries), all in the same order."""
    pairs = flatten_cv_skills(cv)
    names = [skill for skill, _ in pairs]
    tiers = [tier for _, tier in pairs]
    entries = [asdict(ground(skill)) for skill in names]
    return names, tiers, entries
