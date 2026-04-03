import json

import requests
from bs4 import BeautifulSoup

base_url = "https://www.bestjobs.eu/api/proxy/v2/jobs?limit=2"


def bestjobs_V2(domain = None, experience = None, work_type = None, location = None):
    filtered_url = url_apply_filters(domain, experience, work_type, location)
    response, soup = site_response(filtered_url)
    #print(response.text)
    #print(soup)
    json_url_parse(response)



def url_apply_filters(domain = None, experience = None, work_type = None, location = None):
    return base_url

#title, company, location, slug / slug => w type, descr, exp level, logo


def json_url_parse(response):
    data = response.json()

    for item in data['items']:
        print(item['title'])
        print(item['companyName'])
        print(item['locations'][1]['slug'])
        print(item['slug'])
        print(item['salary'])



def site_response(url): #ERROR HANDLING
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response, soup

bestjobs_V2()