import requests

def get_response(url: str, timeout: int = 10):
    try:
        response = requests.get(url, timeout=timeout)

        if not response.ok:
            print(f"Server returned error code: {response.status_code}")
            return None, None

        return response.text

    except requests.RequestException as e:
        print(f"Network error: {e}")
        return None, None