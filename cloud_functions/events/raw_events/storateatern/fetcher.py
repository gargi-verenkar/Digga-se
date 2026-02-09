import itertools

from raw_events.fetcher import EventFetcher, normalize_datetime
from raw_events.storateatern.api import get_events, get_description
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class StoraTeaternFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)

    def get_events(self) -> list[Event]:
        events_by_month = get_events()
        event_shows = [
            self.to_event(event_in_month) for event_in_month in events_by_month
        ]
        return list(itertools.chain(*event_shows))

    @staticmethod
    def to_event(event_data: dict) -> list[Event]:
        result = []
        for event in event_data.get("events"):
            venue = Venue(
                city="Göteborg",
                address_text="Kungsparken 1",
                zipcode=41136,
                name="Stora Teatern",
                coordinates=Coordinates(
                    latitude=57.70260450000001, longitude=11.97059319999994
                ),
            )
            source_data = SourceEvent(
                name=StoraTeaternFetcher.get_title(event),
                event_id=str(event.get("id"))
                + event.get("event_id")
                + event.get("event_time"),
                description=get_description(event.get("event_url")),
                start_datetime=normalize_datetime(event.get("started_at"), "CET"),
                end_datetime=None,
                venue=venue,
                currency="SEK",
                price_range=[
                    float(event.get("price").get("event-price")),
                ],
                ticket_link=event.get("event_url"),
                status=("Cancelled" if event.get("show_cancelled") else "Active"),
                sold_out=None,
                date_tickets_sale_start=normalize_datetime(event.get("published")),
                organizer="Stora Teatern",
                tags=None,
                image=StoraTeaternFetcher.get_image(event),
                artists=None,
                explicit_category = None
            )
            result.append(Event(source="storateatern", source_data=source_data))
        return result

    @staticmethod
    def get_title(event: dict) -> str or None:
        title = event.get("title").get("full_title") if event.get("title") else None
        if event.get("subtitle").get("full_subtitle"):
            title = title + " - " + event.get("subtitle").get("full_subtitle")
        return title

    @staticmethod
    def get_image(event: dict) -> str or None:
        if event.get("images"):
            return event.get("images")[0].get("image_thumbnail_url")
        return None
