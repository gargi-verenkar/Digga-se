import requests
import json
import gzip

def get_events(api_key: str) -> list[dict]:
    headers = {
        "X-API-Key": api_key,
        "Accept": "application/json",
    }
    response = requests.get(
        url="https://www.capitolbio.se/api/digga",
        headers=headers,
    )
    response.raise_for_status()
    data = json.loads(response.content)
    events = []
    for item in data:
        event = {
            "id": str(item.get("id")),
            "title": item.get("movieName"),
            "start_time": item.get("showTimeStart"),
            "end_time": item.get("showTimeEnd"),
            "price_min": item.get("ticketPrice", {}).get("min"),
            "price_max": item.get("ticketPrice", {}).get("max"),
            "description": item.get("description"),
            "booking_url": item.get("bookingUrl"),
            "image_url": item.get("imageUrl"),
        }
        events.append(event)
    return events