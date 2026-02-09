import requests
from bs4 import BeautifulSoup
from enum import Enum

class EventType(Enum):
    CONCERT = "concert"
    CLASSICAL = "classical"

BASE_URL = "https://www.glennmillercafe.se"
CURRENCY = "SEK"
TIMEZONE = "CET"

CONCERTS_PATH = "/konserter/"
CONCERTS_TIME = "20:00"
CONCERTS_TITLE = "Jazz på Glenn Miller Café"
CONCERTS_CATEGORY = "Concert"
CONCERTS_GENRE = ["jazz"]
CONCERTS_PRICE_RANGE = [70, 210]
CONCERTS_EVENT_LINK = "https://www.glennmillercafe.se/konserter/"

CLASSICAL_PATH = "/klassiska-konserter/"
CLASSICAL_TIME = "20:00"
CLASSICAL_TITLE = "Klassiskt på Glenn Miller Café"
CLASSICAL_CATEGORY = "Concert"
CLASSICAL_GENRE = ["klassiskt"]
CLASSICAL_PRICE_RANGE = [70, 210]
CLASSICAL_EVENT_LINK = "https://www.glennmillercafe.se/klassiska-konserter/"

EVENT_CONFIG = {
    EventType.CONCERT: {
        "title": CONCERTS_TITLE,
        "time": CONCERTS_TIME,
        "price": CONCERTS_PRICE_RANGE,
        "category": CONCERTS_CATEGORY,
        "genre": CONCERTS_GENRE,
        "link": CONCERTS_EVENT_LINK,
    },
    EventType.CLASSICAL: {
        "title": CLASSICAL_TITLE,
        "time": CLASSICAL_TIME,
        "price": CLASSICAL_PRICE_RANGE,
        "category": CLASSICAL_CATEGORY,
        "genre": CLASSICAL_GENRE,
        "link": CLASSICAL_EVENT_LINK,
    }
}

def get_events() -> list[dict]:
    events = get_concerts(EventType.CLASSICAL)
    events += get_concerts(EventType.CONCERT)
    return events

def get_concerts(event_type: EventType) -> list[dict]:
    url = get_event_url(event_type)
    if url is None:
        return []
    soup = get_soup(url)
    if soup is None:
        return []

    return scrape_events(soup, event_type)

def get_event_url(event_type: EventType) -> str | None:
    if event_type == EventType.CONCERT:
        return BASE_URL + CONCERTS_PATH
    elif event_type == EventType.CLASSICAL:
        return BASE_URL + CLASSICAL_PATH
    else:
        return None

def get_soup(url: str) -> BeautifulSoup | None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

    return BeautifulSoup(response.content, "html.parser")

def scrape_events(soup: BeautifulSoup, event_type: EventType) -> list[dict]:
    events = []
    for event_div in soup.find_all("div", class_="KaEeLN"):
        date = get_date(event_div)
        if date is None:
            continue

        description = get_description(event_div)
        if description is None:
            continue

        event = populate_event_data(event_type, date, description)
        events.append(event)
    return events

def populate_event_data(event_type: EventType, date: str, description: str) -> dict:
    config = EVENT_CONFIG[event_type]
    return {
        "title": config["title"],
        "description": description,
        "time": config["time"],
        "date": date,
        "timezone": TIMEZONE,
        "price": config["price"],
        "currency": CURRENCY,
        "category": config["category"],
        "genre": config["genre"],
        "link": config["link"],
    }

def get_date(event_div):
    date_tag = event_div.find("h2")
    if date_tag:
        return date_tag.get_text(separator=" ", strip=True)
    # for some reason somtimes the date uses p instead of h2, but then it's the second p
    p_tags = event_div.find_all("p")
    if len(p_tags) >= 2:
        return p_tags[1].get_text(separator=" ", strip=True)
    return None 

def get_description(event_div):
    description_tag = event_div.find("p")
    if description_tag:
        return description_tag.get_text(separator=" ", strip=True)
    return None