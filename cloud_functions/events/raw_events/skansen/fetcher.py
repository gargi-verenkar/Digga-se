import html
from builtins import list

from raw_events.skansen.api import get_events
from raw_events.fetcher import EventFetcher, normalize_zipcode, normalize_datetime
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class SkansenFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)

    def get_events(self) -> list[Event]:
        events_data = get_events()
        return [self.to_event(event) for event in events_data]

    @staticmethod
    def to_event(event_data: dict) -> Event | None:
        venue = Venue(
            city="Stockholm",
            address_text="Djurgårdsslätten 49-51",
            zipcode=normalize_zipcode("11521"),
            name="Skansen",
            coordinates=Coordinates(
                latitude=59.3262463,
                longitude=18.1023263
            )
        )
        # Combine date and time for start and end
        date = event_data.get("date")
        start_time = event_data.get("start_time")
        end_time = event_data.get("end_time")

        start_datetime = normalize_datetime(f"{date} {start_time}", "CET") if date and start_time else None
        end_datetime = normalize_datetime(f"{date} {end_time}", "CET") if date and end_time else None
        source_data = SourceEvent(
            name=event_data.get("title"),
            event_id=event_data.get("id"),
            description=html.unescape(event_data.get("description")),
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            venue=venue,
            currency="SEK",
            price_range=None,
            ticket_link=event_data.get("url"),
            status="Active",
            sold_out=None,
            date_tickets_sale_start=None,
            organizer=venue.name,
            tags=event_data.get("tags"),
            image=event_data.get("image"),
            artists=None,
            explicit_category=None
        )
        return Event(source="skansen", source_data=source_data)
