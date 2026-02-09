import html
import itertools
from builtins import list

from raw_events.nortic.api import get_shows
from raw_events.fetcher import EventFetcher, normalize_zipcode, normalize_datetime
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class NorticFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)

    def get_events(self) -> list[Event]:
        events = get_shows().get("events")
        event_shows = [self.to_event(event) for event in events]
        return list(itertools.chain(*event_shows))

    @staticmethod
    def to_event(event_data: dict) -> list[Event]:
        result = []
        for show in event_data.get("shows"):
            latitude = (
                float(show.get("arenaLatitude")) if show.get("arenaLatitude") else None
            )
            longitude = (
                float(show.get("arenaLongitude"))
                if show.get("arenaLongitude")
                else None
            )
            venue = Venue(
                city=show.get("arenaCity"),
                address_text=show.get("arenaAddress"),
                zipcode=normalize_zipcode(show.get("arenaPostcode")),
                name=show.get("arenaName"),
                coordinates=(
                    Coordinates(latitude=latitude, longitude=longitude)
                    if (latitude and longitude)
                    else None
                ),
            )
            
            source_data = SourceEvent(
                name=show.get("name") or event_data.get("title"),
                event_id=str(show.get("id")) if show.get("id") else None,
                description=(
                    html.unescape(html.unescape(event_data.get("description")))
                    if event_data.get("description")
                    else None
                ),
                start_datetime=normalize_datetime(show.get("startDate"), "CET"),
                end_datetime=normalize_datetime(show.get("closeDate"), "CET"),
                venue=venue,
                currency="SEK",
                price_range=[show.get("minPrice"), show.get("maxPrice")],
                ticket_link=show.get("link"),
                status=None,  # information is missing in the API
                sold_out=False,
                date_tickets_sale_start=normalize_datetime(
                    show.get("releaseDate"), "CET"
                ),
                organizer=event_data.get("organizerName"),
                tags=(
                    event_data.get("keys").split(",")
                    if event_data.get("keys")
                    else None
                ),
                image=event_data.get("imageUrl"),
                artists=None,
                explicit_category = None
            )

            result.append(Event(source="nortic", source_data=source_data))
        return result
