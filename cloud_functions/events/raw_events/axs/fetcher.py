from raw_events.fetcher import EventFetcher, normalize_datetime, normalize_zipcode
from raw_events.models import Event, SourceEvent, Venue, Coordinates
import html

from raw_events.axs.api import get_events


class AxsFetcher(EventFetcher):
    def __init__(self, gcp_project: str, pubsub_topic: str, axs_api_key: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)
        self.axs_api_key = axs_api_key

    def get_events(self) -> list[Event]:
        events = get_events(self.axs_api_key)
        return [AxsFetcher.to_event(event) for event in events]

    @staticmethod
    def to_event(event_data: dict) -> Event:
        location = event_data.get("venue")
        venue = Venue(
            city=location.get("city"),
            address_text=location.get("address"),
            zipcode=normalize_zipcode(location.get("postalCode")),
            name=location.get("title"),
            coordinates=(
                Coordinates(
                    latitude=float(location.get("latitude")),
                    longitude=float(location.get("longitude")),
                )
                if (location.get("latitude") and location.get("longitude"))
                else None
            ),
        )
        source_data = SourceEvent(
            name=event_data.get("title").get("eventTitleText"),
            event_id=event_data.get("eventId"),
            description=(
                html.unescape(event_data.get("description"))
                if event_data.get("description")
                else None
            ),
            start_datetime=(
                normalize_datetime(event_data.get("eventDateTimeUTC"))
                if event_data.get("eventDateTimeUTC") != "TBD"
                else None
            ),
            end_datetime=None,
            venue=venue,
            currency=event_data.get("currency"),
            price_range=AxsFetcher.get_pricerange(event_data),
            ticket_link=event_data.get("ticketing").get("eventUrl"),
            status="Active",
            sold_out=event_data.get("ticketing").get("status") == "Sold Out",
            date_tickets_sale_start=normalize_datetime(
                event_data.get("onsaleDateTimeUTC")
            ),
            organizer=AxsFetcher.get_organizer(event_data),
            tags=None,
            image=AxsFetcher.get_image(event_data),
            artists=AxsFetcher.get_artist(event_data),
            explicit_category = None
        )
        return Event(source="axs", source_data=source_data)

    @staticmethod
    def get_pricerange(event_data: dict) -> list or None:
        if event_data.get("ticketPrice"):
            return [
                float(event_data.get("ticketPriceLow")),
                float(event_data.get("ticketPriceHigh")),
            ]
        return None

    @staticmethod
    def get_image(event_data: dict) -> str or None:
        # Otherwise get it from media
        media = (
            event_data.get("relatedMedia")
            if event_data.get("relatedMedia")
            else event_data.get("media")
        )
        if media:
            first_key = next(iter(media))
            return media[first_key].get("file_name")
        return None

    @staticmethod
    def get_artist(event_data: dict) -> list[str] or None:
        associations = event_data.get("associations")
        artists = [artist.get("name") for artist in associations.get("headliners")]
        artists += [artist.get("name") for artist in associations.get("supportingActs")]
        artists += [
            artist.get("name") for artist in associations.get("additionalPerformers")
        ]
        if artists:
            return artists
        return None

    @staticmethod
    def get_organizer(event_data: dict) -> str or None:
        promoters = event_data.get("promoters")
        if not promoters:
            return None
        return promoters[0].get("promoterName")
