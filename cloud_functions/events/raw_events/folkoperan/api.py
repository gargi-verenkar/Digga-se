import requests
import json


def get_events(api_key: str) -> list[dict]:
    response = requests.get(
        f"https://eventapi.tix.se/v2/Events?key={api_key}", timeout=10
    )
    response.raise_for_status()
    data = json.loads(response.content)
    return data
