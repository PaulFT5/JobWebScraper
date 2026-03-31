import os
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

config_dir = Path(__file__).parent.parent / "config/filters_config.json"

def filter_config_reader():
    with open(config_dir, 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data


def bestjobs_url_builder(location = None, domain = None, type_of_work = None, experience = None, keywords = None):
    filtered_url = "https://www.bestjobs.eu/locuri-de-munca"

    if location:
        filtered_url += "-in-" + location
    if domain:
        filtered_url += "/" + domain
    if type_of_work:
        filtered_url += "/" + type_of_work
    if experience:
        filtered_url += "/" + experience
    if keywords:
        filtered_url += "/" + keywords

    return filtered_url


def links_list(soup): #get links from page
    links = []
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if "/loc-de-munca/" in href and href not in links:
            links.append(href)
            break #remove after testing
    return links


def get_job_title(soup):
    return soup.find('h2').get_text()
    print(title)
    return title

def get_company_name(soup):
    return soup.find('h3').get_text()

def get_salary(soup):
    div =  soup.find("div", class_="ml-2")
    if div.find("strong"):
        return div.find("strong").get_text()
    return None

def get_experience_level(soup):
    return soup.find(class_="hover:text-ink").get_text().split()[0]


#url = bestjobs_url_builder()
#response = requests.get(url)
#soup = BeautifulSoup(response.content, "html.parser")
#links_list(soup)
