import requests
import logging

def get_events() -> list[dict]:
    # Specific key for Stadsteater
    api_key = "af0d719507534f9e"
    url = f"https://eventapi.tix.se/v2/Events?key={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Tixly API Error for Helsingborg Stadsteater: {e}")
        return []