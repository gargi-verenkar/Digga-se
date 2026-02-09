import itertools

from slugify import slugify
from raw_events.fetcher import EventFetcher, normalize_datetime
from raw_events.ravinen.api import get_events
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class RavinenFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)

    def get_events(self) -> list[Event]:
        events_data = get_events()
        event_shows = [self.to_events(event_data) for event_data in events_data]
        return list(itertools.chain(*event_shows))

    @staticmethod
    def to_events(event_data: dict) -> list[Event]:
        result = []
        for event in event_data.get("occasions"):
            venue = Venue(
                city="Båstad",
                address_text="Kattviksvägen 231",
                zipcode=26991,
                name="Ravinen Kulturhus",
                coordinates=Coordinates(
                    latitude=56.44754015508936, longitude=12.796900063915688
                ),
            )
            source_data = SourceEvent(
                name=event_data.get("description"),
                event_id=f"{event_data.get('id')}-{event.get('time')}",
                description=event_data.get("translation")[0].get("description"),
                start_datetime=normalize_datetime(event.get("time", "CET")),
                end_datetime=None,
                venue=venue,
                currency="SEK",
                price_range=RavinenFetcher.get_price(event_data),
                ticket_link=f"https://ravinenkultur.entryevent.se/ticketshop/events/{slugify(event_data.get('description'))}",
                status="Active",
                sold_out=False,
                date_tickets_sale_start=None,
                organizer="Ravinen Kulturhus",
                tags=None,
                image=(
                    f"https://norrviken.entryevent.se/shopapi/allotmentimage/{event_data.get('imageFileName')}"
                    if event_data.get("imageFileName")
                    else None
                ),
                artists=None,
                explicit_category = None
            )
            result.append(Event(source="ravinen", source_data=source_data))
        return result

    @staticmethod
    def get_price(event: dict):
        prices = []

        for article in event.get('articles', []):
            price = article.get('price', {}).get('amountInclVat')
            if price is not None:
                prices.append(price)

        if not prices:
            return None

        min_price = min(prices)
        max_price = max(prices)

        return [min_price] if min_price == max_price else [min_price, max_price]
