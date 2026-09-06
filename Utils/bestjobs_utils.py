import sqlite3
from pathlib import Path

import requests
from bs4 import BeautifulSoup
DB_PATH = Path(__file__).resolve().parent.parent / "Scraper" / "JobsDatabase.sqlite"
print(DB_PATH)


def reset_availability(cursor, conn):
    cursor.execute(
        "Update Jobs set available = 0 where available = 1"
    )
    conn.commit()

def check_slug_already_present(cursor, conn, slug_check):
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM Jobs WHERE slug = ?)", (slug_check,)
    )
    result = cursor.fetchone()
    return bool(result[0])

def site_response(url): #ERROR HANDLING
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response, soup

def database_connect():
    conn = sqlite3.connect(DB_PATH)
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
        elements = description.find_all(["p", "li"])
        parts = []
        for el in elements:
            text = el.get_text(strip=True)
            if not text:
                continue
            if el.name == "li":
                parts.append(f"- {text}")
            else:
                parts.append(text)
        full_text = "\n\n".join(parts)
        return full_text
    except AttributeError:
        return None