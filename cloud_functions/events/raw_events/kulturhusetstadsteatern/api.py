import requests

def get_events() -> list[dict]:
    response = requests.get(
        url="https://kulturhusetstadsteatern.se/api/v2/all-drupal-event-data"
    )
    response.raise_for_status()

    events = []
    for event in response.json().values():
        event_id = event.get("nid")    
        if not event_id:
            continue  # Skip this event if nid is missing or None

        response = requests.get(
            url=f"https://kulturhusetstadsteatern.se/api/v2/event/{event_id}"
        )
        response.raise_for_status()
        events.append(response.json())
    return events