import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "scraper" / "bestjobs" / "config.json"


def get_bestjobs_filters():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    filters = data.get("filters", {})

    work_types_list = []
    for name, id_val in filters.get("work_types", {}).items():
        work_types_list.append({"id": id_val, "name": name})

    domains_list = []
    for name, id_val in filters.get("domains", {}).items():
        domains_list.append({"id": id_val, "name": name})

    return {
        "cities": filters.get("cities", []),
        "work_types": work_types_list,
        "domains": domains_list,
    }