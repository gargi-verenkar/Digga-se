import gzip
import json

import requests

STATUSES = {
    "0": "Active",
    "1": "Active",
    "2": "Active",
    "6": "Active",
    "7": "Cancelled",
}


def get_events(username: str, password: str) -> list[dict]:
    response = requests.get(
        url="https://pft.eventim.com/serve/657-pcq4wf", auth=(username, password)
    )
    response.raise_for_status()
    data = json.loads(gzip.decompress(response.content))
    return data.get("eventserie")
