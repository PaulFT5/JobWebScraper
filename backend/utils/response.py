import requests
from bs4 import BeautifulSoup

def get_response(url): #ERROR HANDLING
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response, soup