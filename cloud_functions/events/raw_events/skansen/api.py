import requests
import json

def get_events() -> list[dict]:
    response = requests.get(
        url="https://skansen.se/wp-json/api/v1/events",
    )
    response.raise_for_status()
    data = json.loads(response.content)
    events = []
    items = data.get("data", {}).get("items", [])
    for item in items:
        event_id = str(item.get("id"))
        title = item.get("title")
        description = item.get("description")
        url = item.get("url")
        # the url has a staging in it which makes it unusable, we need the skansen without staging
        if url:
            url = url.replace("staging.", "", 1)
        image = item.get("thumbnail")	
        dates = item.get("dates", [])
        tags = [tag.get("name") for tag in item.get("tags", []) if tag.get("name")]
        dates = item.get("dates", [])
        for date_obj in dates:
            for date_str, times_list in date_obj.items():
                for time_entry in times_list:
                    times = time_entry.get("times", [])
                    for t in times:
                        event = {
                            "id": event_id + "-" + date_str,
                            "title": title,
                            "description": description,
                            "date": date_str,
                            "start_time": t.get("start"),
                            "end_time": t.get("end"),
                            "url": url,
                            "image": image,
                            "tags": tags,
                        }
                        events.append(event)
    return events