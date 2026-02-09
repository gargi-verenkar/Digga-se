import requests
import logging

def get_events() -> list[dict]:
    api_key = "661e6ba156164746" # Arena Key
    url = f"https://eventapi.tix.se/v2/Events?key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Tixly API Error for Helsingborg Arena: {e}")
        return []