import requests
import json
from datetime import date, timedelta


def get_events(username: str, password: str) -> list[dict]:
    all_events = []
    page = 1
    
    while True:
        response = requests.get(
            f"https://foundationapi.ebiljett.nu/v1/106/events?fromDate={(date.today() - timedelta(days=3)).isoformat()}&pageNumber={page}",
            auth=(username, password),
        )
        response.raise_for_status()
        data = response.json()
        
        # Get events from the "items" field
        events = data.get("items", [])
        all_events.extend(events)
        
        # Check if there are more pages
        if not data.get("has_next_page", False):
            break
        
        page += 1
    
    # Fetch details for each event
    return [
        _get_event_details(event.get("identifier"), username, password)
        for event in all_events
    ]


def _get_event_details(event_id: str, username: str, password: str) -> dict:
    response = requests.get(
        f"https://foundationapi.ebiljett.nu/v1/106/events/{event_id}",
        auth=(username, password),
    )
    response.raise_for_status()
    return response.json()
