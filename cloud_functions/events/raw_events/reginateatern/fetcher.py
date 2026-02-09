import logging

from raw_events.fetcher import EventFetcher, normalize_datetime, normalize_zipcode
from raw_events.models import Event, SourceEvent, Venue, Coordinates
import html

from raw_events.reginateatern.api import get_events


class ReginateaternFetcher(EventFetcher):
    def __init__(
        self, gcp_project: str, pubsub_topic: str, username: str, password: str
    ) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)
        self.username = username
        self.password = password

    def get_events(self) -> list[Event]:
        events = get_events(self.username, self.password)
        return [ReginateaternFetcher.to_event(event) for event in events]

    @staticmethod
    def to_event(event_data: dict) -> Event:
        venue = Venue(
            city="Uppsala",
            address_text="Trädgårdsgatan 6",
            zipcode=75309,
            name="Reginateatern",
            coordinates=Coordinates(
                latitude=59.85705662784672,
                longitude=17.636584238062436,
            ),
        )
        source_data = SourceEvent(
            name=event_data.get("name"),
            event_id=str(event_data.get("identifier")),
            description=(
                html.unescape(event_data.get("long_description"))
                if event_data.get("long_description")
                else None
            ),
            start_datetime=normalize_datetime(event_data.get("event_date"), "CET"),
            end_datetime=None,
            venue=venue,
            currency="SEK",
            price_range=None,
            ticket_link=event_data.get("url"),
            status="Active",
            sold_out=event_data.get("sales").get("available") == 0,
            date_tickets_sale_start=normalize_datetime(
                event_data.get("sales_start"), "CET"
            ),
            organizer="Reginateatern",
            tags=None,
            image=event_data.get("image_url"),
            artists=None,
            explicit_category = None
        )
        return Event(source="reginateatern", source_data=source_data)
