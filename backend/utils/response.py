import requests
from bs4 import BeautifulSoup

def get_response(url: str, timeout: int = 10):
    try:
        response = requests.get(url, timeout=timeout)

        if not response.ok:
            print(f"Server returned error code: {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.content, "html.parser")
        return response, soup

    except requests.RequestException as e:
        print(f"Network error: {e}")
        return None, None