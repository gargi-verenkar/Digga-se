import requests
from google.cloud import secretmanager

def get_events() -> list[dict]:
    # Get credentials from Secret Manager
    client = secretmanager.SecretManagerServiceClient()
    
    response = requests.get(
        url=f"https://www.berwaldhallen.se/api/feeds/calendar",
        timeout=10
    )
    response.raise_for_status()
    return response.json().get("data", [])
