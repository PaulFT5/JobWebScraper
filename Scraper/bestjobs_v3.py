import asyncio
import sqlite3
import time
import aiohttp
import requests
from bs4 import BeautifulSoup

from Utils.LLM import LLM_activation

#limit url usages
limit = 7
BASE_LIMIT_URL = f"https://www.bestjobs.eu/api/proxy/v2/jobs?limit={limit}"
BASE_URL = "https://www.bestjobs.eu/loc-de-munca/"
CITIES = ["timisoara", "brasov", "bucuresti"]

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

    async with aiohttp.ClientSession() as session:
        for url, domain_name, domain_id, city, work_type_name, work_type_id in url_list:
            #I
            slug_list = json_parser(url, domain_name, domain_id, city, work_type_name, work_type_id, cursor, conn)
            # II and III
            additional_info(slug_list, cursor, conn)
            # III
            #skills_extraction()

    conn.close()
    end = time.time()
    length = end - start
    print("Time taken: ", length)

#I. insert source, slug, title, company name, salary, est salary
def json_parser(url, domain_name, domain_id, city, work_type_name, work_type_id, cursor, conn):
    response, soup = site_response(url)
    data = response.json()
    slug_list =[]
    new_slugs = []

    for item in data['items']:
        slug = item['slug']
        slug_list.append(slug)

        if check_slug_already_present(cursor, conn, slug):
            #set availability to 1
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
    for slug in slug_list:
        url = BASE_URL + slug
        response, soup = site_response(url)

        if response.status_code == 200:
            experience_level = get_experience_level(soup)
            description = get_description(soup)
            #skills_json = skills_extraction(description)

            cursor.execute(
                "UPDATE Jobs SET experience_level = ?, description = ? WHERE slug = ?",
                (experience_level, description ,slug)
            )

    conn.commit()


#HELPER FUNCTIONS

def skills_extraction(description):
    prompt = "You are a professional recruiter analyzing a job description. Extract all skills required or preferred by the employer from the job description text below and return them as a JSON object. Follow these rules strictly: Hard skills — concrete, verifiable skills tied to performing the job: tools, software, systems, certifications, methodologies, or specialized domain knowledge (examples across fields: Python, SQL, SAP, Google Ads, GDPR compliance, phlebotomy, payroll processing, AutoCAD). For each skill, classify it as 'required' or 'preferred' based on how it is presented in the text (e.g. listed under Requirements/Must-have vs. Nice-to-have/Preferred/Plus). If the posting does not distinguish between the two, classify all extracted skills as 'required'. Separately, extract required_experience_level for the role as a whole, based on any explicit statement in the text (e.g. '3+ years', 'entry-level position', 'senior role'). Use one of: entry_level (0–2 years), junior (2–3 years), mid_level (3–5 years), senior (5+ years). If no experience level is stated, use 'not_specified'. Languages — return any spoken/written language requirements explicitly stated (e.g. 'fluent in English'). If none are stated, return an empty list. Return only valid JSON. No explanation, no markdown, no code fences."
    data = LLM_activation(prompt, description)
    return data

def reset_availability(cursor, conn):
    cursor.execute(
        "Update Jobs set available = 0 where available = 1"
    )
    conn.commit()

def check_slug_already_present(cursor, conn, slug_check):
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM Jobs WHERE slug = ?)", (slug_check,)
    )
    result = cursor.fetchone()
    return bool(result[0])

def site_response(url): #ERROR HANDLING
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response, soup

def database_connect():
    conn = sqlite3.connect('JobsDatabase.sqlite')
    cursor = conn.cursor()
    return cursor, conn

def get_experience_level(soup):
    try:
        return soup.select_one("div.ml-2 a").get_text().split()[0]
    except AttributeError:
        return None

# def get_description(soup):
#     try:
#         description = soup.find("div", class_="mt-8 pt-8 border-t border-input break-words prose job-description text-sm")
#         paragraphs = description.find_all("p")
#         full_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
#         return full_text
#     except AttributeError:
#         return None

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

asyncio.run(parser())