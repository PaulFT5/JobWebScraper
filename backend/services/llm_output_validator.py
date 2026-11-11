"""Shared validation of LLM skill-extraction replies.

Both pipelines (job skill extraction and the CV parser) pass the raw LLM
reply through this module, so every stored or returned skill list has the
same shape: a list of unique, non-empty, stripped strings.
"""
import json


class LLMOutputError(ValueError):
    """Base error for an unusable LLM reply."""


class MalformedJSONError(LLMOutputError):
    """The reply is not valid JSON."""


class InvalidShapeError(LLMOutputError):
    """The reply is valid JSON but not in the expected shape."""


JOB_SKILLS_KEY = "required_skills"
CV_SKILLS_KEY = "hard_skills"
CV_LANGUAGES_KEY = "languages"
UNKNOWN_TIER = "unknown"

# Variants the LLM has returned before, mapped to the canonical cv_tier_map names.
CV_TIER_ALIASES = {
    "entry_level": "entry",
    "entry-level": "entry",
    "mid_level": "mid",
    "mid-level": "mid",
    "middle": "mid",
}


def parse_json_object(raw):
    """Strip optional markdown code fences, parse the JSON and require an object."""
    if not isinstance(raw, str):
        raise MalformedJSONError(f"expected text, got {type(raw).__name__}")

    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.rstrip()
        if text.endswith("```"):
            text = text[:-3]

    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise MalformedJSONError(str(error)) from error

    if not isinstance(data, dict):
        raise InvalidShapeError(f"expected a JSON object, got {type(data).__name__}")
    return data


def clean_skill_list(values, field):
    """Keep non-empty stripped strings, drop case-insensitive duplicates, keep order."""
    if not isinstance(values, list):
        raise InvalidShapeError(f"'{field}' must be a list, got {type(values).__name__}")

    cleaned = []
    seen = set()
    for value in values:
        if not isinstance(value, str):
            continue
        skill = " ".join(value.split())
        key = skill.casefold()
        if skill and key not in seen:
            seen.add(key)
            cleaned.append(skill)
    return cleaned


def validate_job_skills(raw):
    """Job extraction reply -> list of skills.

    Expected reply: {"required_skills": ["Python", "SQL"]}
    """
    data = parse_json_object(raw)
    if JOB_SKILLS_KEY not in data:
        raise InvalidShapeError(f"missing key '{JOB_SKILLS_KEY}', got {list(data.keys())}")
    return clean_skill_list(data[JOB_SKILLS_KEY], JOB_SKILLS_KEY)


def cv_tiers():
    """Canonical CV tiers, highest first, then 'unknown' (from config.json cv_tier_map)."""
    from backend.matching.config import get_config

    tier_map = get_config()["seniority"]["cv_tier_map"]
    ordered = sorted(tier_map, key=lambda tier: tier_map[tier], reverse=True)
    return tuple(ordered) + (UNKNOWN_TIER,)


def validate_cv_skills(raw, tiers=None):
    """CV parser reply -> {"hard_skills": {tier: [...]}, "languages": [...]}.

    Every tier key is always present. A skill listed in several tiers keeps
    only the highest one; 'unknown' counts as lowest, so any dated tier wins.
    """
    tiers = tuple(tiers) if tiers is not None else cv_tiers()
    data = parse_json_object(raw)

    hard_skills = data.get(CV_SKILLS_KEY)
    if not isinstance(hard_skills, dict):
        raise InvalidShapeError(f"'{CV_SKILLS_KEY}' must be an object, got {type(hard_skills).__name__}")

    by_tier = {tier: [] for tier in tiers}
    for key, values in hard_skills.items():
        tier = CV_TIER_ALIASES.get(str(key).strip().lower(), str(key).strip().lower())
        if tier not in by_tier:
            raise InvalidShapeError(f"unknown CV tier '{key}', expected one of {list(tiers)}")
        by_tier[tier].extend(clean_skill_list(values, f"{CV_SKILLS_KEY}.{key}"))

    result = {}
    seen = set()
    for tier in tiers:
        kept = []
        for skill in clean_skill_list(by_tier[tier], f"{CV_SKILLS_KEY}.{tier}"):
            if skill.casefold() not in seen:
                seen.add(skill.casefold())
                kept.append(skill)
        result[tier] = kept

    languages = clean_skill_list(data.get(CV_LANGUAGES_KEY, []), CV_LANGUAGES_KEY)
    return {CV_SKILLS_KEY: result, CV_LANGUAGES_KEY: languages}
