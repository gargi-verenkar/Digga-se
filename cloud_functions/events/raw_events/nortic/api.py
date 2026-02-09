import requests


def get_shows() -> dict:
    response = requests.get(url="https://www.nortic.se/api/json/shows")
    response.raise_for_status()
    return response.json()
