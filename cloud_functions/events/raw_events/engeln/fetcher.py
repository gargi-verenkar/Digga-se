import itertools

from raw_events.fetcher import EventFetcher, normalize_datetime, normalize_zipcode
from raw_events.engeln.api import get_events
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class EngelnFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)

    def get_events(self) -> list[Event]:
        events = get_events()
        return [self.to_event(event) for event in events]

    @staticmethod
    def to_event(event_data: dict) -> Event:
        # now there is only one other venue so if the place exist it is this other place
        if event_data.get("place"):
            venue = Venue(
                city="Stockholm",
                address_text="Kornhamnstorg 59B",
                zipcode=normalize_zipcode("11127"),
                name="Kolingen",
                coordinates=Coordinates(
                    latitude=59.322583, longitude=18.0695287
                ),
            )
        else:
            venue = Venue(
                city="Stockholm",
                address_text="Kornhamnstorg 59B",
                zipcode=normalize_zipcode("11127"),
                name="Engelen",
                coordinates=Coordinates(
                    latitude=59.322583, longitude=18.0695287
                ),
            )
        source_data = SourceEvent(
            name=event_data.get("title"),
            event_id=str(event_data.get("time")),
            description=None,
            start_datetime=normalize_datetime(event_data.get("time"), "CET"),
            end_datetime=None,
            venue=venue,
            currency="SEK",
            price_range=[
                event_data.get("price"),
            ],
            ticket_link=None,
            status="Active",
            sold_out=None,
            date_tickets_sale_start=None,
            organizer="Engelen",
            tags=None,
            image=event_data.get("image"),
            artists=None,
            explicit_category="Concert"
        )
        return Event(source="engeln", source_data=source_data)
