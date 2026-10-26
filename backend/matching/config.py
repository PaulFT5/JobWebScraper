import hashlib
import json
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ESCO_FILES = ("skills_en.csv", "skill_Pillars.csv", "skill_Hierarchy.csv")
REQUIRED_KEYS = {
    "esco": ("version", "language", "data_folder"),
    "seniority": ("job_level_map", "cv_tier_map", "multipliers_by_tiers_below", "unknown_cv_tier_or_no_job_level"),
}


@lru_cache(maxsize=1)
def get_config():
    with open(CONFIG_PATH, mode="r", encoding="utf-8") as file:
        config = strip_metadata(json.load(file))

    validate(config)
    config["fingerprint"] = make_fingerprint(config)
    config["esco"]["data_folder"] = PROJECT_ROOT / config["esco"]["data_folder"]
    return freeze(config)


def strip_metadata(value):
    if isinstance(value, dict):
        return {key: strip_metadata(item) for key, item in value.items() if key != "metadata"}
    return value


def validate(config):
    for group, keys in REQUIRED_KEYS.items():
        if group not in config:
            raise ValueError(f"config.json: missing group '{group}'")
        for key in keys:
            if key not in config[group]:
                raise ValueError(f"config.json: missing '{group}.{key}'")

    esco = config["esco"]
    if esco["language"] != "en":
        raise ValueError("config.json: esco.language must be 'en'")
    folder = PROJECT_ROOT / esco["data_folder"]
    missing = [name for name in ESCO_FILES if not (folder / name).is_file()]
    if missing:
        raise ValueError(f"config.json: {folder} is missing {', '.join(missing)}")

    seniority = config["seniority"]
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



def make_fingerprint(config):
    text = json.dumps(config, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    return value