import gzip
import json

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Status values https://developer.ticketmaster.com/products-and-docs/apis/discovery-feed/#json-feed-response
STATUSES = {
    "onsale": "Active",
    "offsale": "Active",
    "rescheduled": "Active",
    "postponed": "Active",
    "cancelled": "Cancelled",
}

session = requests.Session()
session.mount(
    "https://",
    HTTPAdapter(
        max_retries=Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False,
        )
    ),
)


def get_events(api_key: str, new_api_key: str) -> list[dict]:
    response = session.get(
        url="https://app.ticketmaster.com/discovery-feed/v2/events.json",
        params={"apikey": api_key, "countryCode": "SE"},
    )
    response.raise_for_status()
    data = json.loads(gzip.decompress(response.content))
    details = get_details(api_key, new_api_key)
    return join_events_and_details(data.get("events"), details)


# Necessary because of weird API design in Ticketmaster
def get_details(api_key: str, new_api_key: str) -> dict:
    events = get_events_from_internation_discovery_api(new_api_key)
    details = {}
    for event in events:
        legacy_event_id = get_legacy_event_id(api_key, event.get("id"))
        if legacy_event_id is not None:
            event_details = get_event_details(new_api_key, event.get("id"))
            details[legacy_event_id] = event_details
    return details


def get_events_from_internation_discovery_api(new_api_key: str) -> list[dict]:
    events = []
    while True:
        response = session.get(
            url="https://app.ticketmaster.eu/mfxapi/v2/events",
            params={
                "apikey": new_api_key,
                "countryCode": "SE",
                "domain": "sweden",
                "country_ids": 752,
                "rows": 250,
                "start": len(events),
            },
        )
        response.raise_for_status()
        data = response.json()
        events.extend(data.get("events"))
        if len(events) >= data.get("pagination").get("total"):
            break
    return events


def get_legacy_event_id(api_key: str, event_id: str) -> str:
    response = session.get(
        url=f"https://app.ticketmaster.com/discovery/v2/events/legacy/MFX-SE-{event_id}",
        params={"apikey": api_key, "locale": "*"},
    )
    return None if (response.status_code >= 400) else response.json().get("id")


def get_event_details(new_api_key: str, event_id: str) -> dict:
    response = session.get(
        url=f"https://app.ticketmaster.eu/mfxapi/v2/events/{event_id}",
        params={"apikey": new_api_key, "domain": "sweden"},
    )
    response.raise_for_status()

    json_response = response.json()
    return {
        "description": json_response.get("description", ""),
        "on_sale_date": json_response.get("on_sale_date", {}),
    }


def join_events_and_details(events: list[dict], details: dict) -> list[dict]:
    updated_events = []
    for event in events:
        event_detail = details.get(event.get("eventId"), {})
        event["description"] = event_detail.get("description", "")
        event["on_sale_date"] = event_detail.get("on_sale_date", {})
        updated_events.append(event)
    return updated_events
