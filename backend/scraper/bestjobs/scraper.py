import datetime
import json
import time
from functools import lru_cache
from pathlib import Path
from backend.database.repositories.job_repositories import check_existing_slug, add_description_experience, \
    add_new_jobs, mark_available
from backend.utils.response import get_response


@lru_cache(maxsize=1)
def load_config():
    config_path = Path(__file__).resolve().parent.parent / "bestjobs" / "config.json"
    with config_path.open(encoding="utf-8") as file:
        return json.load(file)

def get_experience_level(soup):
    try:
        return soup.select_one("div.ml-2 a").get_text().split()[0]
    except AttributeError:
        return None

def get_description(soup):
    try:
        description = soup.find("div", class_="mt-8 pt-8 border-t border-input break-words prose job-description text-sm")
        elements = description.find_all(["p", "li"])
        parts = []
        for el in elements:
            text = el.get_text(strip=True)
            if not text:
                continue
            if el.name == "li":
                parts.append(f"- {text}")
            else:
                parts.append(text)
        full_text = "\n\n".join(parts)
        return full_text
    except AttributeError:
        return None

def json_response(url, domain_name, domain_id, city, work_type_name, work_type_id, cursor, conn):
    response, soup = get_response(url)

    if not soup or not response:
        return []

    data = response.json()
    slug_list =[]
    new_slugs = []

    scraped_date = datetime.date.today().isoformat()

    for item in data['items']:
        slug = item['slug']
        slug_list.append(slug)

        if check_existing_slug(cursor, slug):
            continue

        new_slugs.append(slug)
        ad_link = f"https://www.bestjobs.eu/ro/loc-de-munca/{slug}"

        add_new_jobs(cursor, "bestjobs", slug, item["title"], item["companyName"],
                     item["salary"], item["estimatedSalary"], work_type_id, work_type_name,
                     ad_link, city, domain_id, domain_name, scraped_date)

    mark_available(cursor, slug_list)
    conn.commit()
    return new_slugs

def additional_info(slug_list, cursor, conn):
    config = load_config()
    delay = config["api"]["delay_between_requests_sec"]
    base_url = config["api"]["base_url"]

    stats = {"fetched_ok": 0, "http_failed": 0, "description_missing": 0}

    for slug in slug_list:
        url = base_url + slug

        response, soup = get_response(url)
        if not soup or not response:
            stats["http_failed"] += 1
            continue

        experience_level = get_experience_level(soup)
        description = get_description(soup)

        if not description:
            stats["description_missing"] += 1
            add_description_experience(cursor, experience_level, None, slug)
        else:
            add_description_experience(cursor, experience_level, description, slug)
            stats["fetched_ok"] += 1

        time.sleep(delay)

        conn.commit()
    return stats
