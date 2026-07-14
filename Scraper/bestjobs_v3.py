import asyncio
import sqlite3
import time
import aiohttp
import requests
from bs4 import BeautifulSoup

#limit url usages
limit = 3
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

# I, II: Url preparation

#Makes a list of url + city
def generate_urls():
    urls = []
    for city in CITIES:
        for domain in DOMAINS.values():
            urls.append(f"{BASE_LIMIT_URL}&location%5B%5D={city}&domain%5B%5D={domain}")
    return urls



#Function that connects the PARSER part
async def parser():
    start = time.time()
    url_list = generate_urls()
    async with aiohttp.ClientSession() as session:
        for url in url_list:
            json_parser(url)
            # II
            # III
    end = time.time()
    length = end - start
    print(length)

#insert source, slug, title, company name, salary, est salary
def json_parser(url):
    response, soup = site_response(url)
    cursor, conn = database_connect()
    data = response.json()

    for item in data['items']:
        slug = item['slug']
        ad_link = f"https://www.bestjobs.eu/ro/loc-de-munca/{slug}"

        cursor.execute(
            "INSERT OR IGNORE INTO Jobs (source, slug, title, company_name, salary, est_salary, ad_link, available) VALUES (?, ?, ?, ?, ?, ?, ?, true)",
            ("bestjobs", slug, item['title'], item['companyName'], item['salary'], item['estimatedSalary'], ad_link)
        )
    conn.commit()
    conn.close()




#HELPER FUNCTIONS

def site_response(url): #ERROR HANDLING
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response, soup

def database_connect():
    conn = sqlite3.connect('JobsDatabase.sqlite')
    cursor = conn.cursor()
    return cursor, conn

asyncio.run(parser())