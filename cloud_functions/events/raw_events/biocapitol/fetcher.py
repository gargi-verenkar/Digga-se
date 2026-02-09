import html
from builtins import list

from raw_events.biocapitol.api import get_events
from raw_events.fetcher import EventFetcher, normalize_zipcode, normalize_datetime
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class BioCapitolFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str, api_key: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)
        self.api_key = api_key

    def get_events(self) -> list[Event]:
        events_data = get_events(api_key=self.api_key)
        return [self.to_event(event) for event in events_data]

    @staticmethod
    def to_event(event_data: dict) -> Event | None:
        venue = Venue(
            city="Stockholm",
            address_text="Sankt Eriksgatan 82",
            zipcode=normalize_zipcode("11362"),
            name="Bio Capitol",
            coordinates=Coordinates(
                latitude=59.3403221,
                longitude=18.0375362
            )
        )

        source_data = SourceEvent(
            name=html.unescape(event_data.get("title")),
            event_id=event_data.get("id"),
            description=html.unescape(event_data.get("description")),
            start_datetime=normalize_datetime(event_data.get("start_time")),
            end_datetime=normalize_datetime(event_data.get("end_time")),
            venue=venue,
            currency="SEK",
            price_range=[
                event_data.get("price_min"),
                event_data.get("price_max"),
            ],
            ticket_link=event_data.get("booking_url"),
            status="Active",
            sold_out=False,
            date_tickets_sale_start=None,
            organizer="Bio Capitol",
            tags=None,
            image=event_data.get("image_url"),
            artists=None,
            explicit_category=None
        )
        return Event(source="biocapitol", source_data=source_data)
