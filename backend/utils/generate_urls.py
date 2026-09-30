import json
from pathlib import Path
from cachetools.func import lru_cache

@lru_cache(maxsize=1)
def load_config():
    config_path = Path(__file__).resolve().parent.parent / "scraper" / "bestjobs" / "config.json"
    with config_path.open(encoding="utf-8") as file:
        return json.load(file)

def generate_urls():
    config = load_config()
    cities = config["filters"]["cities"]
    domains = config["filters"]["domains"]
    work_types = config["filters"]["work_types"]

    base_url = config["api"]["json_response_url"]
    limit = config["api"]["default_limit"]
    base_limit_url = f"{base_url}?limit={limit}"

    urls = []
    for city in cities:
        for domain_name, domain_id in domains.items():
            for work_type_name, work_type_id in work_types.items():
                urls.append((
                    f"{base_limit_url}&location%5B%5D={city}&domain%5B%5D={domain_id}&employmentTypes%5B%5D={work_type_id}",
                    domain_name, domain_id,
                    city,
                    work_type_name, work_type_id
                ))
    return urls
