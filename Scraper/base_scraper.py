import requests
from bs4 import BeautifulSoup

#get all links ->

url = "https://www.bestjobs.eu/locuri-de-munca?_lat=45.718961&_lon=21.322763&pageNr=eyJ0eXBlIjoib2Zmc2V0IiwicGFnZSI6Miwic2l6ZSI6MjQsIm9mZnNldCI6MjR9"
#url = "https://www.bestjobs.eu/loc-de-munca/payable-accountant-with-german?rid=7c6d81d2-844d-441e-9af0-e057a6bac006&pos=1"
response = requests.get(url)
print(response.status_code)
soup = BeautifulSoup(response.content, "html.parser")
#print(soup.prettify())

for link in soup.find_all('a'):
    print(link.get('href'))

h2 = soup.find("h2", class_="mt-1 mb-3 text-6xl font-semibold leading-tight tracking-tighter break-words")

#if h2:
    #link = h2.find("a")
    #print(link.get_text(strip=True))  # job title
    #print(link["href"])