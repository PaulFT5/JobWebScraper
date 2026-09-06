import asyncio
import time
import aiohttp
from Utils.bestjobs_utils import site_response, check_slug_already_present, get_experience_level, get_description, \
    database_connect, reset_availability
from Utils.email_log_sender import sender

#limit url usages
limit = 500
BASE_LIMIT_URL = f"https://www.bestjobs.eu/api/proxy/v2/jobs?limit={limit}"
BASE_URL = "https://www.bestjobs.eu/loc-de-munca/"
CITIES = ["timisoara", "brasov", "bucuresti"] #

DOMAINS = {
    "IT": 9,
    "Engineering": 14,
    "HR": 18,
    "Production & Logistics": 5,
    "Public Service": 20,
    "Administrative & Secretarial": 8,
    "Medical": 15,
    "Management": 13,
    "Marketing": 10,
}

WORK_TYPE = {
#     se ia url-ul, filtrare pe baza de asta, return db
#     &employmentTypes%5B%5D=1
    "Full time": 1,
    "Part time":2,
    "Internship": 4,
}

# I, II: Url preparation

#Makes a list of url + city
def generate_urls():
    urls = []
    for city in CITIES:
        for domain_name, domain_id in DOMAINS.items():
            for work_type_name, work_type_id in WORK_TYPE.items():
                urls.append((
                    f"{BASE_LIMIT_URL}&location%5B%5D={city}&domain%5B%5D={domain_id}&employmentTypes%5B%5D={work_type_id}",
                    domain_name, domain_id,
                    city,
                    work_type_name, work_type_id
                )) #tuple of elements
    return urls


#Function that connects the PARSER part
async def parser():
    start = time.time()
    url_list = generate_urls()
    cursor, conn = database_connect()
    reset_availability(cursor, conn)

    totals = {"new_jobs": 0, "fetched_ok": 0, "http_failed": 0, "description_missing": 0}

    async with aiohttp.ClientSession() as session:
        for url, domain_name, domain_id, city, work_type_name, work_type_id in url_list:
            #I
            slug_list = json_parser(url, domain_name, domain_id, city, work_type_name, work_type_id, cursor, conn)
            # II and III
            info_stats = additional_info(slug_list, cursor, conn)

            totals["new_jobs"] += len(slug_list)
            for key in ("fetched_ok", "http_failed", "description_missing"):
                totals[key] += info_stats[key]

    conn.close()
    end = time.time()
    totals["duration_sec"] = int(round(end - start, 2))
    body = (
        f"New jobs found:        {totals['new_jobs']}\n"
        f"Detail pages fetched:  {totals['fetched_ok']}\n"
        f"Detail pages failed:   {totals['http_failed']}  (non-200 response)\n"
        f"Descriptions missing:  {totals['description_missing']}  (page fetched but description not found)\n"
        f"Run duration:          {totals['duration_sec']}s"
    )
    try:
        sender("Daily Skill Extraction Summary", body)
    except Exception as e:
        print(f"WARNING: failed to send summary email: {e}")
    print(body)

    print("Time taken: ", totals["duration_sec"])

#I. insert source, slug, title, company name, salary, est salary
def json_parser(url, domain_name, domain_id, city, work_type_name, work_type_id, cursor, conn):
    #print(url)
    response, soup = site_response(url)
    data = response.json()
    #print(f"{domain_name}/{city}/{work_type_name}: {len(data.get('items', []))} items, status {response.status_code}")
    slug_list =[]
    new_slugs = []

    for item in data['items']:
        slug = item['slug']
        slug_list.append(slug)

        if check_slug_already_present(cursor, conn, slug):
            cursor.execute(
                "UPDATE Jobs SET available = 1 WHERE slug = ?",
                (slug,)
            )
            continue

        new_slugs.append(slug)
        ad_link = f"https://www.bestjobs.eu/ro/loc-de-munca/{slug}"


        cursor.execute(
            "INSERT OR IGNORE INTO Jobs (source, slug, title, company_name, salary, est_salary, work_type, worktype_name, ad_link, available, city, domain, domain_name) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, true, ?, ?, ?)",
            ("bestjobs", slug, item['title'], item['companyName'], item['salary'], item['estimatedSalary'],
             work_type_id, work_type_name, ad_link, city, domain_id, domain_name)
        )

    cursor.executemany(
        "UPDATE Jobs SET available = 1 WHERE slug = ?",
        [(s,) for s in slug_list]
    )
    conn.commit()
    return new_slugs

def additional_info(slug_list, cursor, conn):
    stats = {"fetched_ok": 0, "http_failed": 0, "description_missing": 0}
    for slug in slug_list:
        url = BASE_URL + slug
        response, soup = site_response(url)

        if response.status_code == 200:
            experience_level = get_experience_level(soup)
            description = get_description(soup)

            if description is None:
                stats["description_missing"] += 1

            cursor.execute(
                "UPDATE Jobs SET experience_level = ?, description = ? WHERE slug = ?",
                (experience_level, description,slug)
            )
            stats["fetched_ok"] += 1
        else:
            stats["http_failed"] += 1
    conn.commit()
    return stats

if __name__ == "__main__":
    asyncio.run(parser())