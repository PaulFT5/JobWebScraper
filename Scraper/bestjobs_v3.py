import asyncio
import sqlite3
import time
import aiohttp
import requests
from bs4 import BeautifulSoup

#limit url usages
limit = 1
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
        for domain in DOMAINS.values():
            for work_type in WORK_TYPE.values():
                urls.append((f"{BASE_LIMIT_URL}&location%5B%5D={city}&domain%5B%5D={domain}&employmentTypes%5B%5D={work_type}", domain, city, work_type))
    return urls


#Function that connects the PARSER part
async def parser():
    start = time.time()
    url_list = generate_urls()
    cursor, conn = database_connect()
    async with aiohttp.ClientSession() as session:
        for url, domain, city, work_type in url_list:
            #I
            slug_list = json_parser(url, domain, city, work_type, cursor, conn)
            # II
            additional_info(slug_list, cursor, conn)
            # III
            skills_extraction()
    conn.close()
    end = time.time()
    length = end - start
    print(length)

#I. insert source, slug, title, company name, salary, est salary
def json_parser(url, domain, city, work_type, cursor, conn):
    response, soup = site_response(url)
    data = response.json()
    slug_list =[]

    for item in data['items']:
        slug = item['slug']
        slug_list.append(slug)
        ad_link = f"https://www.bestjobs.eu/ro/loc-de-munca/{slug}"

        cursor.execute(
            "INSERT OR IGNORE INTO Jobs (source, slug, title, company_name, salary, est_salary, work_type, ad_link, available, city, domain) VALUES (?, ?, ?, ?, ?, ?, ?, ?, true, ?, ?)",
            ("bestjobs", slug, item['title'], item['companyName'], item['salary'], item['estimatedSalary'],work_type, ad_link, city, domain)
        )
    conn.commit()
    return slug_list

def additional_info(slug_list, cursor, conn):
    for slug in slug_list:
        url = BASE_URL + slug
        response, soup = site_response(url)

        if response.status_code == 200:
            experience_level = get_experience_level(soup)
            description = get_description(soup)

            cursor.execute(
                "UPDATE Jobs SET experience_level = ?, description = ? WHERE slug = ?",
                (experience_level, description, slug)
            )

    conn.commit()

def skills_extraction():
    return  None


#HELPER FUNCTIONS

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

def get_description(soup):
    try:
        description = soup.find("div", class_="mt-8 pt-8 border-t border-input break-words prose job-description text-sm")
        paragraphs = description.find_all("p")
        full_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
        return full_text
    except AttributeError:
        return None

asyncio.run(parser())