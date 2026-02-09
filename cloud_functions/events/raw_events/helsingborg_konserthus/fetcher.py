import html
import itertools
from raw_events.helsingborg_konserthus.api import get_events
from raw_events.fetcher import EventFetcher, normalize_datetime
from raw_events.models import Event, SourceEvent, Venue, Coordinates

class HelsingborgKonserthusFetcher(EventFetcher):
    def get_events(self) -> list[Event]:
        events_data = get_events()
        event_shows = [self.to_events(event) for event in events_data]
        return list(itertools.chain(*event_shows))
    
    @staticmethod
    def to_events(event_data: dict) -> list[Event]:
        result = []
        for date_item in event_data.get("Dates", []):
            venue = Venue(
                city="Helsingborg",
                address_text="Roskildegatan 1",
                zipcode=int("25221"),
                name="Helsingborgs Konserthus",
                coordinates=Coordinates(latitude=56.0494, longitude=12.6891)
            )
            
            unique_id = f"helsingborg_konserthus-{date_item.get('EventId')}"

            source_data = SourceEvent(
                name=event_data.get("Name"),
                event_id=unique_id,
                description=html.unescape(event_data.get("LongDescription", "") or ""),
                start_datetime=normalize_datetime(date_item.get("StartDate")),
                end_datetime=normalize_datetime(date_item.get("EndDate")),
                venue=venue,
                currency="SEK",
                price_range=[float(date_item.get("MinPrice") or 0), float(date_item.get("MaxPrice") or 0)],
                ticket_link=date_item.get("PurchaseUrls")[0].get("Link") if date_item.get("PurchaseUrls") else None,
                status="Active",
                sold_out=date_item.get("SoldOut"),
                date_tickets_sale_start=normalize_datetime(date_item.get("OnlineSaleStart")),
                organizer="Helsingborg Konserthus",
                tags=None,
                image=event_data.get("EventImagePath"),
                artists=None,
                explicit_category=None
            )
            
            result.append(Event(source="helsingborg_konserthus", source_data=source_data))
        
        return result