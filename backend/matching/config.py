import hashlib
import json
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ESCO_FILES = ("skills_en.csv", "skill_Pillars.csv", "skill_Hierarchy.csv")

REQUIRED_KEYS = {
    "esco": ("version", "language", "data_folder"),
    "grounding": ("methods", "fuzzy_threshold", "gap_acceptance_min", "fuzzy_min_length", "embedding_floor"),
    "seniority": ("job_level_map", "cv_tier_map", "multipliers_by_tiers_below", "unknown_cv_tier_or_no_job_level"),
}

# Grounding method -> letter in the fingerprint prefix ("0" when the method is off).
METHOD_CODES = (("exact", "E"), ("fuzzy", "F"), ("embedding", "M"))


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_config():
    with open(CONFIG_PATH, mode="r", encoding="utf-8") as file:
        config = strip_metadata(json.load(file))

    validate(config)
    config["fingerprint"] = make_fingerprint(config)
    config["grounding_fingerprint"] = make_grounding_fingerprint(config)
    config["esco"]["data_folder"] = PROJECT_ROOT / config["esco"]["data_folder"]
    return freeze(config)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def strip_metadata(value):
    if isinstance(value, dict):
        return {key: strip_metadata(item) for key, item in value.items() if key != "metadata"}
    return value


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate(config):
    validate_required_keys(config)
    validate_esco(config["esco"])
    validate_grounding(config["grounding"])
    validate_seniority(config["seniority"])


def validate_required_keys(config):
    for group, keys in REQUIRED_KEYS.items():
        if group not in config:
            raise ValueError(f"config.json: missing group '{group}'")
        for key in keys:
            if key not in config[group]:
                raise ValueError(f"config.json: missing '{group}.{key}'")


def validate_esco(esco):
    if esco["language"] != "en":
        raise ValueError("config.json: esco.language must be 'en'")
    folder = PROJECT_ROOT / esco["data_folder"]
    missing = [name for name in ESCO_FILES if not (folder / name).is_file()]
    if missing:
        raise ValueError(f"config.json: {folder} is missing {', '.join(missing)}")


def validate_grounding(grounding):
    methods = grounding["methods"]
    known = {name for name, _ in METHOD_CODES}
    if not isinstance(methods, list) or not methods:
        raise ValueError("config.json: grounding.methods must be a non-empty list")
    unknown = [name for name in methods if name not in known]
    if unknown:
        raise ValueError(f"config.json: grounding.methods has unknown names: {', '.join(unknown)}")


def validate_seniority(seniority):
    for map_name in ("job_level_map", "cv_tier_map"):
        for level, value in seniority[map_name].items():
            if not isinstance(value, int) or not 0 <= value <= 3:
                raise ValueError(f"config.json: seniority.{map_name}.{level} must be an integer from 0 to 3")

    multipliers = seniority["multipliers_by_tiers_below"]
    if set(multipliers) != {"0", "1", "2", "3"}:
        raise ValueError("config.json: seniority.multipliers_by_tiers_below needs exactly the keys '0' to '3'")
    values = {**multipliers, "unknown_cv_tier_or_no_job_level": seniority["unknown_cv_tier_or_no_job_level"]}
    for name, value in values.items():
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"config.json: seniority multiplier '{name}' must be between 0 and 1")


# ---------------------------------------------------------------------------
# Fingerprints
# ---------------------------------------------------------------------------
def make_fingerprint(config):
    """Hash of the whole config (every group)."""
    text = json.dumps(config, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def make_grounding_fingerprint(config):
    """Readable method prefix + hash of the settings that change grounding results, e.g. 'EF0-3b7e91c2'."""
    grounding = config["grounding"]
    methods = grounding["methods"]
    prefix = "".join(code if name in methods else "0" for name, code in METHOD_CODES)

    settings = {
        "esco_version": config["esco"]["version"],
        "fuzzy_threshold": grounding["fuzzy_threshold"],
        "gap_acceptance_min": grounding["gap_acceptance_min"],
        "fuzzy_min_length": grounding["fuzzy_min_length"],
    }
    if "embedding" in methods:
        settings["embedding_floor"] = grounding["embedding_floor"]
        settings["model"] = config["model"]["name"]
        settings["revision"] = config["model"]["revision"]

    text = json.dumps(settings, sort_keys=True)
    return f"{prefix}-{hashlib.sha256(text.encode('utf-8')).hexdigest()[:8]}"


# ---------------------------------------------------------------------------
# Freezing (read-only config)
# ---------------------------------------------------------------------------
def freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    return value