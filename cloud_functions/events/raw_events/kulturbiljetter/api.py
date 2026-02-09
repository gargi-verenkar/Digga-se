import requests


def get_events(api_key: str) -> list[dict]:
    response = requests.get(
        url="https://kulturbiljetter.se/api/v3/events",
        headers={"Authorization": f"Token {api_key}"},
    )
    response.raise_for_status()

    events = []
    for event in response.json().values():
        event_id = event.get("event_id")
        response = requests.get(
            url=f"https://kulturbiljetter.se/api/v3/events/{event_id}",
            headers={"Authorization": f"Token {api_key}"},
        )
        response.raise_for_status()
        events.append(response.json())
    return events
