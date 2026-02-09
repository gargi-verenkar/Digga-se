import requests
import json
import html
from bs4 import BeautifulSoup


def get_events() -> list[dict]:
    response = requests.get(
        "https://storateatern.se/uploads/json-cache/Event/current.json", timeout=10
    )
    response.raise_for_status()
    data = json.loads(response.content)
    return data.get("data")


def get_description(url: str) -> str or None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Extracting all links
    description_paragraphs = [
        tag.text
        for tag in soup.find("div", attrs={"class": "content--event"}).find_all("p")
    ]

    return html.unescape("\n \n ".join(description_paragraphs))
