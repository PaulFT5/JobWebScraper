import csv
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from backend.matching.config import get_config


@lru_cache(maxsize=1)
def load_all_csv(folder=None):
    hierarchy = load_hierarchy(folder)
    skills = load_skills(folder)
    skill_pillars = load_skill_pillars(folder)

    return hierarchy, skills, skill_pillars


def load_hierarchy(folder=None):
    path = esco_folder(folder) / "skill_Hierarchy.csv"
    return read_csv(path)


def load_skills(folder=None):
    path = esco_folder(folder) / "skills_en.csv"
    rows = read_csv(path)
    skills_by_uri = {}

    for row in rows:
        uri = row.get("conceptUri")
        if not uri:
            continue
        # ESCO lists some concepts twice; keep the most recently modified row
        stored = skills_by_uri.get(uri)
        if stored and parse_date(stored["modifiedDate"]) >= parse_date(row.get("modifiedDate")):
            continue
        skills_by_uri[uri] = {
            "preferredLabel": row.get("preferredLabel"),
            "altLabels": split_labels(row.get("altLabels")),
            "hiddenLabels": split_labels(row.get("hiddenLabels")),
            "skillType": row.get("skillType"),
            "reuseLevel": row.get("reuseLevel"),
            "description": row.get("description"),
            "modifiedDate": row.get("modifiedDate"),
        }

    return skills_by_uri


def load_skill_pillars(folder=None):
    path = esco_folder(folder) / "skill_Pillars.csv"
    rows = read_csv(path)
    parent_by_uri = {}

    for row in rows:
        uri = row.get("conceptUri")
        broader_uri = row.get("broaderUri")
        if not uri or not broader_uri:
            continue
        if uri not in parent_by_uri:
            parent_by_uri[uri] = []
        parent_by_uri[uri].append({
            "broaderUri": broader_uri,
            "broaderType": row.get("broaderType"),
        })

    return parent_by_uri


def esco_folder(folder):
    return Path(folder) if folder else get_config()["esco"]["data_folder"]


def split_labels(cell):
    return [label.strip() for label in (cell or "").splitlines() if label.strip()]


def parse_date(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)


def read_csv(path):
    with open(path, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        data = tuple(reader)
    return data


if __name__ == "__main__":
    hierarchy, skills, skill_pillars = load_all_csv()
    print(f"hierarchy rows: {len(hierarchy)}")
    print(f"skills: {len(skills)}")
    print(f"concepts with pillar links: {len(skill_pillars)}")