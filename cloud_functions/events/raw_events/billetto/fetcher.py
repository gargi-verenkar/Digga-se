import html
from builtins import list

from raw_events.billetto.api import STATES, get_all_public_events
from raw_events.fetcher import EventFetcher, normalize_zipcode
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class BillettoFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str, api_key: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)
        self.api_key = api_key

    def get_events(self) -> list[Event]:
        all_public_events = get_all_public_events(api_key=self.api_key)
        return list(map(self.to_event, all_public_events))

    @staticmethod
    def to_event(event_data: dict) -> Event:
        location = event_data.get("location")
        address = filter(
            None, [location.get("address_line"), location.get("address_line_2")]
        )
        venue = Venue(
            city=location.get("city"),
            address_text=", ".join(address),
            zipcode=normalize_zipcode(location.get("postal_code")),
            name=location.get("location_name"),
            coordinates=Coordinates(
                latitude=location.get("coordinates").get("latitude"),
                longitude=location.get("coordinates").get("longitude"),
            ),
        )
        source_data = SourceEvent(
            name=event_data.get("title"),
            event_id=event_data.get("id"),
            description=(
                html.unescape(event_data.get("description"))
                if event_data.get("description")
                else None
            ),
            start_datetime=event_data.get("startdate"),
            end_datetime=event_data.get("enddate"),
            venue=venue,
            currency=event_data.get("minimum_price").get("currency"),
            price_range=[event_data.get("minimum_price").get("amount_in_cents")],
            ticket_link=event_data.get("url"),
            status=STATES.get(event_data.get("state")),
            sold_out=not event_data.get("availability"),
            date_tickets_sale_start=None,
            organizer=event_data.get("organiser").get("name"),
            tags=None,
            image=event_data.get("image_link"),
            artists=None,
            explicit_category = None
        )
        return Event(source="billetto", source_data=source_data)
