import asyncio
import json
import sqlite3
import os
import json
import aiohttp
import requests
from bs4 import BeautifulSoup
from pip._internal.network import session
from urllib3.util import url
from Utils.bestjobs_utils import get_company_logo, get_experience_level, get_work_type, get_description

with open("filters_config_bestjobs.json", "r", encoding="utf-8") as f:
    config = json.load(f)

base_json_url = config["base_json_url"]
base_url = config["base_url"]

#DATABASE CONNECT
def database_connect():
    conn = sqlite3.connect('JobsDatabase.sqlite')
    cursor = conn.cursor()
    return cursor, conn


def bestjobs(domain = None, experience = None, work_type = None, location = None):
    filtered_url = url_apply_filters(domain, experience, work_type, location)
    response, soup = check_site_response(filtered_url)
    url_response_json_parser(response)
    asyncio.run(ad_parser_async())


def check_site_response(url): #ERROR HANDLING
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response, soup

#move to utils
def url_apply_filters(domain = None, experience = None, work_type = None, location = None):
    return base_json_url

#title, company, location, slug / slug => w type, descr, exp level, logo


def url_response_json_parser(response):
    cursor, conn = database_connect()
    data = response.json()

    for item in data['items']:
        cursor.execute(
            "INSERT OR IGNORE INTO Jobs (source, slug, title, company_name, location, salary, logo, work_type, experience_level, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("bestjobs", item['slug'], item['title'], item['companyName'], item['locations'][0]['slug'], item['salary'],
             None, None, None, None))

    conn.commit()
    conn.close()


async def fetch_job_page(session, slug):
    url = base_url + slug
    sem = asyncio.Semaphore(5)

    async with session.get(url) as response:
        async with sem:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")

    logo = get_company_logo(soup)
    work_type = get_work_type(soup)
    experience = get_experience_level(soup)
    description =get_description(soup)
    #required_skills = get_required_skills(soup)
    #nice_to_have_skills = get_nice_to_have_skills(soup)

    return slug, logo, work_type, experience


async def ad_parser_async():
    cursor, conn = database_connect()
    cursor.execute("SELECT slug FROM Jobs WHERE logo IS NULL OR work_type IS NULL OR experience_level IS NULL OR description IS NULL OR reqired_skills IS NULL OR nice_to_have_skills IS NULL")
    rows = cursor.fetchall()

    slugs = [row[0] for row in rows]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_job_page(session, slug) for slug in slugs]

        results = await asyncio.gather(*tasks)

        for slug, logo, work_type, experience in results:
            cursor.execute(
                "UPDATE Jobs SET logo=?, work_type=?, experience_level=? WHERE slug=?",
                (logo, work_type, experience, slug)
            )

    conn.commit()
    conn.close()

bestjobs()


#def ad_parser(): #based on slug
#     cursor, conn = database_connect()
#     cursor.execute("SELECT slug FROM Jobs WHERE logo IS NULL")
#     rows = cursor.fetchall()
#     for row in rows:
#         url = base_url + row[0]
#         response, soup = check_site_response(url)
#         slug = row[0]
#         logo = get_company_logo(soup)
#         work_type = get_work_type(soup)
#         experience = get_experience_level(soup)
#         cursor.execute("UPDATE Jobs SET logo = ?, work_type = ?, experience_level = ? WHERE slug = ?", (logo, work_type, experience, slug))
#
#     conn.commit()
#     conn.close()