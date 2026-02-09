import itertools

from raw_events.fetcher import EventFetcher, normalize_datetime, normalize_zipcode
from raw_events.glennmillercafe.api import get_events
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class GlennMillerCafeFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)

    def get_events(self) -> list[Event]:
        events = get_events()
        return [self.to_event(event) for event in events]

    @staticmethod
    def to_event(event_data: dict) -> Event:
        venue = Venue(
            city="Stockholm",
            address_text="Brunnsgatan 21A",
            zipcode=normalize_zipcode("11138"),
            name="Glenn Miller Café",
            coordinates=Coordinates(
                latitude=59.3364741, longitude=18.0665454
            ),
        )
        # Construct datetime string safely, handling None values
        event_date = event_data.get("date")
        event_time = event_data.get("time")
        
        datetime_str = None
        if event_date and event_time:
            datetime_str = f"{event_date} {event_time}"
        
        source_data = SourceEvent(
            name=event_data.get("title"),
            event_id=str(event_data.get("date")),
            description=str(event_data.get("description")),
            start_datetime=normalize_datetime(datetime_str, event_data.get("timezone")),
            end_datetime=None,
            venue=venue,
            currency=event_data.get("currency"),
            price_range=event_data.get("price"),
            ticket_link=event_data.get("link"),
            status="Active",
            sold_out=None,
            date_tickets_sale_start=None,
            organizer=venue.name,
            tags=event_data.get("genre"),
            image=None,
            artists=None,
            explicit_category=event_data.get("category")
        )
        return Event(source="glennmillercafe", source_data=source_data)

    @staticmethod
    def get_image(event: dict) -> str or None:
        if event.get("image"):
            return event.get("image")
        return None
