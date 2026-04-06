import json
import sqlite3
import os
import requests
from bs4 import BeautifulSoup

base_json_url = "https://www.bestjobs.eu/api/proxy/v2/jobs?limit=2"
base_url = "https://www.bestjobs.eu/loc-de-munca/"

def bestjobs_V2(domain = None, experience = None, work_type = None, location = None):
    filtered_url = url_apply_filters(domain, experience, work_type, location)
    response, soup = check_site_response(filtered_url)
    #url_response_json_parser(response)
    ad_parser()


def check_site_response(url): #ERROR HANDLING
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response, soup


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

def database_connect():
    conn = sqlite3.connect('JobsDatabase.sqlite')
    cursor = conn.cursor()
    return cursor, conn

def ad_parser(): #based on slug
    cursor, conn = database_connect()
    cursor.execute("SELECT slug FROM Jobs")
    rows = cursor.fetchall()
    for row in rows:
        url = base_url + row[0]
        response, soup = check_site_response(url)
        slug = row[0]
        logo = get_company_logo(soup)
        work_type = get_work_type(soup)
        experience = get_experience_level(soup)
        cursor.execute("UPDATE Jobs SET logo = ?, work_type = ?, experience_level = ? WHERE slug = ?", (logo, work_type, experience, slug))

    conn.commit()
    conn.close()

def get_experience_level(soup):
    return soup.find(class_="hover:text-ink").get_text().split()[0]

def get_work_type(soup):
    soup = soup.find("div", class_="ml-6").get_text()
    return soup.split(";")[0]

def get_company_logo(soup):
    a_tag = soup.find("a", href="#company-widget-box")
    if not a_tag:
        return None
    img_tag = a_tag.find("img")
    if not img_tag:
        return None
    return img_tag.get("src")

async def database_sync():
    return

bestjobs_V2()