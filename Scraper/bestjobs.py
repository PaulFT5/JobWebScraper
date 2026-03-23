
from asyncio import sleep
from Utils import *
import requests
from bs4 import BeautifulSoup

from Utils.bestjobs_utils import bestjobs_url_builder, links_list, get_title

#get all links ->
#check if all the page is loaded

base_url = "https://www.bestjobs.eu/locuri-de-munca"
job_page_url = "https://www.bestjobs.eu"

def bestjobs(location = None, domain = None, type_of_work = None, experience = None, keywords = None):
    #site_response(base_url)
    filtered_url = bestjobs_url_builder(location, domain, type_of_work, experience, keywords)  #filtreaza search
    response, soup = site_response(filtered_url)
    filtered_url_list = links_list(soup) #lista de url-uri
    scrape_ads(filtered_url_list) #returneaza informatii din fiecare link



def site_response(url): #ERROR HANDLING
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response, soup

def scrape_ads(url_list):
    for url in url_list:
        current_url = job_page_url + url
        print(current_url)
        response, soup = site_response(current_url)

        get_title(soup)
        #get_company_name(soup)
        #get_salary(soup)
        #get_work_type(soup)
        #get_work_type(soup)
        #get_location(soup)
        #get_experience_level(soup)

        # descriere - > llm (technical skills, soft skills)
        # scrie csv -> link, title, comapany, salary, work_type, location, experience_level, descriere
        break

bestjobs()




