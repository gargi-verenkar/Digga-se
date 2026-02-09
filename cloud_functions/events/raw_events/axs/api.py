import requests
import json


def get_events(api_key: str) -> list[dict]:
    page = 1
    rows = 100
    response = requests.get(
        f"https://api.axs.com/v1/events?access_token={api_key}&siteId=1&cc=se&page={page}&rows={rows}",
        timeout=10,
    )
    response.raise_for_status()
    data = json.loads(response.content)
    events = data.get("events")
    total = data.get("meta").get("total")
    while total > len(events):
        page += 1
        response = requests.get(
            f"https://api.axs.com/v1/events?access_token={api_key}&siteId=1&cc=se&page={page}&rows={rows}",
            timeout=10,
        )
        response.raise_for_status()
        data = json.loads(response.content)
        events += data.get("events")
    return events
