from datetime import datetime, timedelta
import html
import sys

from raw_events.scalateatern.api import get_events
from raw_events.fetcher import EventFetcher
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class ScalaTeaternFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)

    def get_events(self) -> list[Event]:
        events = get_events()
        return [self.to_event(event) for event in events]

    @staticmethod
    def to_event(event_data: dict) -> Event:
        venue = Venue(
            city="Stockholm",
            address_text="Wallingatan 32",
            zipcode=11124,
            name="Scalateatern",
            coordinates=Coordinates(
                latitude=59.336350448810094, longitude=18.053612301850425
            ),
        )

        start_datetime = datetime.fromtimestamp(
            int(event_data.get("start_date_time"))
        ) - timedelta(hours=1)
        source_data = SourceEvent(
            name=html.unescape(event_data.get("post_title")),
            event_id=event_data.get("id"),
            description=html.unescape(event_data.get("description")),
            start_datetime=start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end_datetime=None,
            venue=venue,
            currency="SEK",
            price_range=list(
                filter(
                    None,
                    [
                        (
                            float(event_data.get("ticket_price_min"))
                            if event_data.get("ticket_price_min")
                            else None
                        ),
                        (
                            float(event_data.get("ticket_price_max"))
                            if event_data.get("ticket_price_max")
                            else None
                        ),
                    ],
                )
            ),
            ticket_link=(
                event_data.get("ticket_link")
                if event_data.get("ticket_link")
                else event_data.get("link")
            ),
            status="Active",
            sold_out=False,
            date_tickets_sale_start=None,
            organizer=None,
            tags=None,
            image=event_data.get("image"),
            artists=None,
            explicit_category = None
        )

        return Event(source="scalateatern", source_data=source_data)
