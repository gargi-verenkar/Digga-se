import requests
import re
import datetime
from bs4 import BeautifulSoup

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "maj": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12
}

def get_events() -> list[dict] or None:
    max_page = get_max_page()
    events = []
    for page in range(1, max_page + 1):
        events.extend(get_events_from_page(page))
    return events

def get_max_page() -> int:
    url = "https://www.engelen.se/livemusik"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return 1  # fallback to 1 if error since there is always at least one page even if it has zero events

    soup = BeautifulSoup(response.content, "html.parser")
    page_numbers = [
        int(a.text)
        for a in soup.find_all("a", class_="page-numbers")
        if a.text.isdigit()
    ]
    return max(page_numbers) if page_numbers else 1

def get_events_from_page(page) -> list[dict] or None:
    url = "https://www.engelen.se/livemusik/page/" + str(page) + "/"
    try:
        response = requests.get(
            url, timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    events = []
    for event_div in soup.find_all("div", class_="single-event"):
        image_url = None
        image_div = event_div.find("div", class_="image")
        if image_div and image_div.has_attr("data-bg-image"):
            image_url = extract_background_image_url(image_div["data-bg-image"])

        place = event_div.find("span", class_="place")
        place_text = place.get_text(strip=True) if place else None

        day_span = event_div.find("span", class_="day")
        month_span = event_div.find("span", class_="month")
        time_span = event_div.find("span", class_="time")
        if not (day_span and month_span and time_span):
            continue  # skip if any date part is missing

        datetime_str = build_datetime(
            day=day_span.get_text(strip=True),
            month=month_span.get_text(strip=True),
            time_str=time_span.get_text(strip=True)
        )

        title_tag = event_div.find("h3")
        title = title_tag.get_text(strip=True) if title_tag else None

        price = get_price(event_div)

        event = {
            "title": title,
            "image": image_url,
            "time": datetime_str,
            "price": price,
            "place": place_text,
        }
        events.append(event)
    return events

def extract_background_image_url(value):
    match = re.search(r'url\([\'"]?(.*?)[\'"]?\)', value)
    if match:
        return match.group(1)
    return None

def get_price(event_div) -> int | None:
    price_text = event_div.find("span", class_="entrence").text.strip()
    if price_text:
        if price_text == "Fri entré":
            return 0
        match = re.search(r"(\d+)", price_text)
        if match:
            return int(match.group(1))
    return None

def build_datetime(day: str, month: str, time_str: str) -> str:
    now = datetime.datetime.now()
    year = now.year
    month_num = MONTHS[month.lower()]
    event_month_day = (month_num, int(day))
    now_month_day = (now.month, now.day)
    # If the event's month/day is before today, use next year
    # because engeln filters out past events on their website
    if event_month_day < now_month_day:
        year += 1
    if time_str == "24:00":
        time_str = "23:59"
    return str(year) + "-" + str(month_num).zfill(2) + "-" + str(int(day)).zfill(2) + " " + time_str
