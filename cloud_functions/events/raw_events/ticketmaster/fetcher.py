import html
from builtins import list

from raw_events.ticketmaster.api import get_events, STATUSES
from raw_events.fetcher import EventFetcher, normalize_zipcode
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class TicketmasterFetcher(EventFetcher):

    def __init__(
        self, gcp_project: str, pubsub_topic: str, api_key: str, new_api_key: str
    ) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)
        self.api_key = api_key
        self.new_api_key = new_api_key

    def get_events(self) -> list[Event]:
        events = get_events(api_key=self.api_key, new_api_key=self.new_api_key)
        return list(map(self.to_event, events))

    @staticmethod
    def to_event(event_data: dict) -> Event:
        latitude = event_data.get("venue").get("venueLatitude")
        longitude = event_data.get("venue").get("venueLongitude")
        venue = Venue(
            city=event_data.get("venue").get("venueCity"),
            address_text=event_data.get("venue").get("venueStreet"),
            zipcode=normalize_zipcode(event_data.get("venue").get("venueZipCode")),
            name=event_data.get("venue").get("venueName"),
            coordinates=(
                Coordinates(latitude=latitude, longitude=longitude)
                if (latitude and longitude)
                else None
            ),
        )
        organizer = (
            event_data.get("promoters")[0].get("promoter").get("name")
            if event_data.get("promoters")
            else None
        )
        source_data = SourceEvent(
            name=event_data.get("eventName"),
            event_id=event_data.get("eventId"),
            description=(
                html.unescape(event_data.get("description"))
                if event_data.get("description")
                else event_data.get("eventInfo")
            ),
            start_datetime=event_data.get("eventStartDateTime"),
            end_datetime=event_data.get("eventEndDateTime"),
            venue=venue,
            currency=event_data.get("currency"),
            price_range=list(
                filter(
                    None,
                    [
                        (
                            float(event_data.get("minPriceWithFees"))
                            if event_data.get("minPriceWithFees")
                            else None
                        ),
                        (
                            float(event_data.get("maxPriceWithFees"))
                            if event_data.get("maxPriceWithFees")
                            else None
                        ),
                    ],
                )
            ),
            ticket_link=event_data.get("primaryEventUrl"),
            status=STATUSES.get(event_data.get("eventStatus")),
            sold_out=None,
            date_tickets_sale_start=event_data.get("on_sale_date", {}).get(
                "value", None
            ),
            organizer=organizer,
            tags=None,
            image=event_data.get("eventImageUrl"),
            artists=None,
            explicit_category = None
        )
        return Event(source="ticketmaster", source_data=source_data)
