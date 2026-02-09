import requests


def get_events() -> list[dict]:
    response = requests.get(
        url="https://www.scalateatern.se/wp-json/scalateatern/v1/upcoming-events"
    )
    response.raise_for_status()

    return response.json()
