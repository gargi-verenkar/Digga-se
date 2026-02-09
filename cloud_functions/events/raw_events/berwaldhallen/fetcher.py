from raw_events.berwaldhallen.api import get_events
from raw_events.fetcher import EventFetcher, normalize_zipcode, normalize_datetime
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class BerwaldhallenFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)

    def get_events(self) -> list[Event]:
        events = get_events()
        return [self.to_event(event) for event in events]

    @staticmethod
    def to_event(event_data: dict) -> Event:
        # Extract location data from API response
        location = event_data.get("location", {})
        address = location.get("address", {})
        
        venue = Venue(
            city=address.get("addressLocality"),
            address_text=address.get("streetAddress"),
            zipcode=normalize_zipcode(address.get("postalCode")),
            name=location.get("name"),
            coordinates=Coordinates(
                latitude=float(location.get("latitude")),
                longitude=float(location.get("longitude"))
            ) if location.get("latitude") and location.get("longitude") else None,
        )
        
        # Extract price and ticket URL from offers
        price_range = [None, None]
        ticket_url = None
        if "offers" in event_data and isinstance(event_data["offers"], dict):
            offers = event_data["offers"]
            
            # Check if priceSpecification exists with minPrice/maxPrice
            price_spec = offers.get("priceSpecification", {})
            if price_spec and "minPrice" in price_spec and "maxPrice" in price_spec:
                # Scenario 1: Use minPrice and maxPrice from priceSpecification
                price_range = [price_spec.get("minPrice"), price_spec.get("maxPrice")]
            else:
                # Scenario 2: Parse the price string (can be single price or range like "170 - 560")
                price = offers.get("price")
                if price:
                    try:
                        if isinstance(price, str) and " - " in price:
                            # Handle price range like "170 - 560"
                            parts = price.split(" - ")
                            min_price = float(parts[0].strip())
                            max_price = float(parts[1].strip())
                            price_range = [min_price, max_price]
                        else:
                            # Handle single price value
                            price_value = float(price) if isinstance(price, str) else price
                            price_range = [price_value, price_value]
                    except (ValueError, TypeError, IndexError):
                        pass
            
            # Extract ticket URL
            ticket_url = offers.get("url")
        
        # Extract sold_out status from availability
        sold_out = None
        if "offers" in event_data and isinstance(event_data["offers"], dict):
            availability = event_data["offers"].get("availability", "")
            if "SoldOut" in availability:
                sold_out = True
            elif "InStock" in availability or "LimitedAvailability" in availability:
                sold_out = False
        
        # Extract event ID from @id field
        event_id = None
        if "@id" in event_data:
            # Extract ID from URL like "https://berwaldhallen.se/event/97314"
            event_id = event_data["@id"].split("/")[-1]
        
        source_data = SourceEvent(
            name=event_data.get("name"),
            event_id=event_id,
            description=event_data.get("description"),
            start_datetime=normalize_datetime(event_data.get("startDate")),
            end_datetime=normalize_datetime(event_data.get("endDate")),
            venue=venue,
            currency="SEK",
            price_range=price_range,
            ticket_link=ticket_url,
            status="Active",
            sold_out=sold_out,
            date_tickets_sale_start=None,
            organizer="Berwaldhallen",
            tags=None,
            image=event_data.get("image"),
            artists=None,
            explicit_category=None
        )
        return Event(source="berwaldhallen", source_data=source_data)
