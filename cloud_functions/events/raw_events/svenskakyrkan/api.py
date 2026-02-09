from datetime import date, timedelta

import requests


def get_places(svk_api_key: str) -> list[dict]:
    places = []
    while True:
        response = requests.get(
            url="https://api.svenskakyrkan.se/platser/v4/place",
            headers={"SvkAuthSvc-ApiKey": svk_api_key},
            params={"offset": len(places), "limit": 500},
        )
        response.raise_for_status()
        payload = response.json()
        places += payload.get("results")
        if len(places) >= payload.get("totalHits"):
            break
    return places


def get_events(ocp_api_key: str) -> list[dict]:
    url = "https://svk-apim-prod.azure-api.net/calendar/v1/event/search"
    params = {
        "is": "musikOchKor",
        "access": "external",
        "from": date.today().isoformat(),
        "to": (date.today() + timedelta(days=31)).isoformat(),
        "expand": "*",
        "limit": 50,
    }
    events = []
    while True:
        response = requests.post(
            url=url, headers={"Ocp-Apim-Subscription-Key": ocp_api_key}, data=params
        )
        response.raise_for_status()
        payload = response.json()
        events += payload.get("result")
        if not payload.get("continuation"):
            break
        params["continuation"] = payload.get("continuation")
    return events
