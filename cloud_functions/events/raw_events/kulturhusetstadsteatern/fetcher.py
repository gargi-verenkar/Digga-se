import html
import itertools
import re
from datetime import datetime
import pytz

from typing import Optional
from raw_events.kulturhusetstadsteatern.api import get_events
from raw_events.fetcher import EventFetcher
from raw_events.models import Event, SourceEvent, Venue
from raw_events.kulturhusetstadsteatern.venue_constants import VENUE_INFO_MAP
from raw_events.kulturhusetstadsteatern.category_constants import CATEGORY_MAP

class KulturhusetstadsteaternFetcher(EventFetcher):
    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)

    def get_events(self) -> list[Event]:
        events = get_events()
        return list(itertools.chain.from_iterable(self.to_event(event) for event in events))

    @staticmethod
    def to_event(event_data: dict) -> list[Event]:
        results = []

        for show in event_data.get("dates", []):
            start_date = show.get("date")
            start_time = show.get("startTime")
            end_time = show.get("endTime")

            if not start_date or not start_time:
                continue

            start_datetime_str = KulturhusetstadsteaternFetcher.get_datetime(start_date, start_time)
            end_datetime_str = None

            if end_time and show.get("showEndTime") is True:
                end_datetime_str = KulturhusetstadsteaternFetcher.get_datetime(start_date, end_time)

            raw_id = show.get("id")
            event_id = str(raw_id) if raw_id is not None else None

            stage_name = show.get("stage")
            if not stage_name:
                continue
            
            venue = KulturhusetstadsteaternFetcher.get_venue(stage_name, show.get("notice"))
            price = KulturhusetstadsteaternFetcher.extract_price(event_data.get("price"))
            category = KulturhusetstadsteaternFetcher.get_category(event_data)

            source_data = SourceEvent(
                name=show.get("eventName"),
                event_id=event_id,
                description=html.unescape(event_data["lead"]) if event_data.get("lead") else None,
                start_datetime=start_datetime_str,
                end_datetime=end_datetime_str,
                venue = venue,
                currency="SEK" if price is not None else None,
                price_range=[price] if price is not None else None,
                ticket_link=show.get("purchaseUrl"),
                status="Active",  # No cancellation info in API
                sold_out=show.get("soldOut"),
                date_tickets_sale_start=None,
                organizer=None,
                tags=None,
                image=event_data.get("image"),
                artists=None,
                explicit_category=category
            )

            results.append(Event(source="kulturhusetstadsteatern", source_data=source_data))

        return results

    @staticmethod
    def extract_price(price_str: str) -> float:
        if not price_str:
            return None
        match = re.search(r"\d+", price_str)
        return float(match.group()) if match else None

    @staticmethod
    def get_datetime(date: str, time: str) -> str:
        sweden_tz = pytz.timezone("Europe/Stockholm")
        naive_local_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        localized_dt = sweden_tz.localize(naive_local_dt)
        utc_dt = localized_dt.astimezone(pytz.UTC)
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def get_venue(stage: str, notice: str) -> Venue:
        if stage.lower() == "parkteatern":
            stage_name = f"{stage} {notice}" if notice else stage
        else:
            stage_name = stage

        info = VENUE_INFO_MAP.get(stage_name.lower())

        venue = Venue(
            city = info.city if info else None,
            address_text = None,
            zipcode = None,
            name = info.venueName if info else stage_name,
            coordinates = None,
        )
        return venue

    @staticmethod
    def get_category(event: dict) -> Optional[str]:
        categories = event.get("tags", {}).get("category", [])
        if not categories:
            return None
        
        title = categories[0].get("title")
        if title is None:
            return None  # No category tag available
        
        category = CATEGORY_MAP.get(title.lower())
        return category