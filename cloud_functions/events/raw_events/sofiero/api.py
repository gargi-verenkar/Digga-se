import requests
import logging

def get_events() -> list[dict]:
    # The confirmed working v2 URL for Sofiero
    api_key = "754673560ec54f62"
    url = f"https://eventapi.tix.se/v2/Events?key={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Tixly API Error for Sofiero: {e}")
        return []