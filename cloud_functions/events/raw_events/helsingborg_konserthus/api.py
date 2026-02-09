import requests
import logging

def get_events() -> list[dict]:
    # Specific API Key for Helsingborg Konserthus
    api_key = "0614a3ecb3484295"
    # Using the confirmed v2 endpoint structure
    url = f"https://eventapi.tix.se/v2/Events?key={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Tixly API Error for Helsingborg Konserthus: {e}")
        return []