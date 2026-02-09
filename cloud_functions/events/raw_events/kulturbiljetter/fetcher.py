import html
import itertools
from builtins import list
from datetime import datetime

from raw_events.kulturbiljetter.api import get_events
from raw_events.fetcher import EventFetcher
from raw_events.models import Event, SourceEvent, Venue


class KulturbiljetterFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str, api_key: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)
        self.api_key = api_key

    def get_events(self) -> list[Event]:
        events = get_events(api_key=self.api_key)
        event_shows = [self.to_event(event) for event in events]
        return list(itertools.chain(*event_shows))

    @staticmethod
    def to_event(event_data: dict) -> list[Event]:
        result = []
        locations = {
            location["location_id"]: location
            for location in event_data.get("locations").values()
        }
        for show in event_data.get("dates").values():
            location = locations.get(show.get("location_id"))
            venue = Venue(
                city=location.get("city"),
                address_text=location.get("street"),
                zipcode=None,
                name=location.get("name"),
                coordinates=None,
            )
            source_data = SourceEvent(
                name=event_data.get("title"),
                event_id=str(show.get("date_id")),
                description=(
                    html.unescape(event_data.get("presentation_long"))
                    if event_data.get("presentation_long")
                    else None
                ),
                start_datetime=datetime.utcfromtimestamp(
                    show.get("unixtime_start")
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                end_datetime=None,
                venue=venue,
                currency="SEK",
                price_range=KulturbiljetterFetcher.get_price_range(event_data.get("price_min"), event_data.get("price_max")),
                ticket_link=show.get("url_checkout"),
                status=None,  # information is missing in the API
                sold_out=show.get("ticket_available") <= 0,
                date_tickets_sale_start=datetime.utcfromtimestamp(
                    event_data.get("unixtime_release")
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                organizer=event_data.get("organizer").get("name"),
                tags=None,
                image=(event_data.get("images") or {}).get("0"),
                artists=None,
                explicit_category = None
            )
            result.append(Event(source="kulturbiljetter", source_data=source_data))
        return result
    
    @staticmethod
    def get_price_range(price_min: str, price_max: str) -> list[float]:
        price_range: list[float] = []

        if price_min is not None:
            price_range.append(float(price_min))

        if price_max is not None:
            price_range.append(float(price_max))

        return price_range
