from backend.database.repositories.job_repositories import check_existing_slug
from backend.utils.response import get_response

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
    #print(url)
    response, soup = get_response(url)
    data = response.json()
    #print(f"{domain_name}/{city}/{work_type_name}: {len(data.get('items', []))} items, status {response.status_code}")
    slug_list =[]
    new_slugs = []

    for item in data['items']:
        slug = item['slug']
        slug_list.append(slug)

        if check_existing_slug(cursor, conn, slug): #include function
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
        time.sleep(0.5)
    conn.commit()
    return stats
