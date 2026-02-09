import requests

# State values https://api.billetto.com/reference/search-publicly-available-events
STATES = {"published": "Active", "canceled": "Cancelled"}


def get_all_public_events(api_key: str) -> list[dict]:
    events = []
    url = "https://billetto.se/api/v3/all_public/events"
    while url:
        response = requests.get(
            url=url, headers={"Api-Keypair": api_key}, params={"limit": 100}
        )
        response.raise_for_status()
        payload = response.json()
        events += payload.get("data")
        url = payload.get("next_url")
    return events
