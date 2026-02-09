import requests

# State values from Event API v1.0 https://developer.tickster.com/documentation
# all lowercase to make sure, the docs says camelcase but we get pascalcase
STATES = {
    "undefined": "Active",
    "notreleased": "Active",
    "releasedforsale": "Active",
    "releasedfornonpublicsale": "Active",
    "salepaused": "Active",
    "saleended": "Active",
    "canceled": "Cancelled",
    "cancelled": "Cancelled",
}


def get_upcoming_events(api_key: str) -> dict:
    response = requests.get(
        url=f"https://api.tickster.com/sv/api/1.0/events/dump/upcoming?key={api_key}"
    )
    response.raise_for_status()

    uri_events = response.json().get("uri")
    if not uri_events:
        return {}

    event_response = requests.get(url=uri_events)
    event_response.raise_for_status()
    return event_response.json()
