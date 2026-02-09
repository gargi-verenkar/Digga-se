import html
from builtins import list

from raw_events.tickster.api import get_upcoming_events, STATES
from raw_events.fetcher import EventFetcher, normalize_zipcode, normalize_datetime
from raw_events.models import Event, SourceEvent, Venue, Coordinates


def calculate_price_range(goods: list):
    prices = []
    for item in goods:
        price = item.get("price", {}).get("includingVat")
        if price:
            price = float(price)
            if price.is_integer():
                price = int(price)
            prices.append(price)
    if prices:
        min_price, max_price = min(prices), max(prices)
        if min_price == max_price:
            return [min_price]
        else:
            return [min_price, max_price]
    return []


class TicksterFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str, api_key: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)
        self.api_key = api_key

    def get_events(self) -> list[Event]:
        upcoming_events = get_upcoming_events(api_key=self.api_key)
        events = upcoming_events.get("events")
        organizers = {
            organizer["id"]: organizer for organizer in upcoming_events["organizers"]
        }
        venues = {venue["id"]: venue for venue in upcoming_events["venues"]}
        result = [
            self.to_event(
                event,
                organizers.get(event["organizerId"]),
                venues.get(event["venueId"]),
            )
            for event in events
        ]
        return list(filter(None, result))

    @staticmethod
    def to_event(
        event_data: dict, organizer_data: dict, venue_data: dict
    ) -> Event | None:
        if venue_data.get("country") != "SE":
            return None
        latitude = venue_data.get("geo", {}).get("latitude")
        longitude = venue_data.get("geo", {}).get("longitude")
        venue = Venue(
            city=venue_data.get("city"),
            address_text=venue_data.get("address"),
            zipcode=normalize_zipcode(venue_data.get("zipCode")),
            name=venue_data.get("name"),
            coordinates=(
                Coordinates(latitude=latitude, longitude=longitude)
                if (latitude and longitude)
                else None
            ),
        )
        source_data = SourceEvent(
            name=event_data.get("name"),
            event_id=event_data.get("id"),
            description=(
                html.unescape(html.unescape(event_data.get("description")))
                if event_data.get("description")
                else None
            ),
            start_datetime=normalize_datetime(event_data.get("start")),
            end_datetime=normalize_datetime(event_data.get("end")),
            venue=venue,
            currency="SEK",
            price_range=calculate_price_range(event_data.get("goods", [])),
            ticket_link=event_data.get("shopUri"),
            status=STATES.get(event_data.get("eventState").lower()),
            sold_out=False,
            date_tickets_sale_start=None,
            organizer=organizer_data.get("name"),
            tags=event_data.get("tags"),
            image=event_data.get("imageUrl"),
            artists=None,
            explicit_category = None
        )
        return Event(source="tickster", source_data=source_data)
