import itertools

from raw_events.fetcher import EventFetcher, normalize_datetime
from raw_events.folkoperan.api import get_events
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class FolkoperanFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str, api_key: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)
        self.api_key = api_key

    def get_events(self) -> list[Event]:
        events_data = get_events(self.api_key)
        event_shows = [self.to_events(event_data) for event_data in events_data]
        return list(itertools.chain(*event_shows))

    @staticmethod
    def to_events(event_data: dict) -> list[Event]:
        result = []
        # All events are duplicated in the Tixly API under a Folkoperan event group, so we need to ignore those
        if event_data.get("Name") == "Folkoperan":
            return result
        for event in event_data.get("Dates"):
            venue = Venue(
                city="Stockholm",
                address_text="Hornsgatan 72",
                zipcode=11821,
                name="Folkoperan",
                coordinates=Coordinates(
                    latitude=59.31858066914292, longitude=18.058402943851373
                ),
            )
            source_data = SourceEvent(
                name=event.get("Name"),
                event_id=str(event.get("EventId")),
                description=None,
                start_datetime=normalize_datetime(event.get("StartDate")),
                end_datetime=normalize_datetime(event.get("EndDate")),
                venue=venue,
                currency="SEK",
                price_range=[
                    float(event.get("MinPrice")),
                    float(event.get("MaxPrice")),
                ],
                ticket_link=event.get("PurchaseUrls")[0].get("Link"),
                status="Active",
                sold_out=event.get("SoldOut"),
                date_tickets_sale_start=normalize_datetime(
                    event.get("OnlineSaleStart")
                ),
                organizer=event.get("Organisation"),
                tags=None,
                image=event_data.get("EventImagePath"),
                artists=None,
                explicit_category = None
            )
            result.append(Event(source="folkoperan", source_data=source_data))
        return result
