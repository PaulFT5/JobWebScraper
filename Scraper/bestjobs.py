from asyncio import sleep
from Utils import *
import requests
from bs4 import BeautifulSoup

from Utils.bestjobs_url_builder import bestjobs_url_builder, links_list

#get all links ->

base_url = "https://www.bestjobs.eu/locuri-de-munca"
job_page_url = "https://www.bestjobs.eu"

def bestjobs(location = None, domain = None, type_of_work = None, experience = None, keywords = None):
    site_response(base_url)
    filtered_url = bestjobs_url_builder(location, domain, type_of_work, experience, keywords)  #filtreaza search
    response, soup = site_response(filtered_url)
    filtered_url_list = links_list(soup) #lista de url-uri
    ad_scraper(filtered_url_list)


def site_response(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response, soup

def ad_scraper(url_list):
    for url in url_list:
        current_url = job_page_url + url
        print(current_url)
        response, soup = site_response(current_url)
        soup = BeautifulSoup(response.content, "html.parser")
        break

bestjobs()




