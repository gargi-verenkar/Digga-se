import itertools
from builtins import list
from datetime import datetime

from raw_events.eventim.api import get_events, STATUSES
from raw_events.fetcher import EventFetcher, normalize_zipcode, normalize_datetime
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class EventimFetcher(EventFetcher):

    def __init__(
        self, gcp_project: str, pubsub_topic: str, username: str, password: str
    ) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)
        self.username = username
        self.password = password

    def get_events(self) -> list[Event]:
        events = get_events(username=self.username, password=self.password)
        event_shows = [self.to_event(event) for event in events]
        return list(itertools.chain(*event_shows))

    @staticmethod
    def to_event(event_data: dict) -> list[Event]:
        events = []
        for event in event_data.get("events"):
            if event.get("eventCountry") != "SE":
                continue
            latitude = event.get("venueLatitude")
            longitude = event.get("venueLongitude")
            venue = Venue(
                city=event.get("eventCity"),
                address_text=event.get("eventStreet"),
                zipcode=normalize_zipcode(event.get("eventZip")),
                name=event.get("eventVenue"),
                coordinates=(
                    Coordinates(latitude=latitude, longitude=longitude)
                    if (latitude and longitude)
                    else None
                ),
            )
            time_offset = datetime.fromisoformat(
                event.get("eventDateIso8601")
            ).strftime("%z")
            # Construct datetime strings safely, handling None values
            event_date = event.get('eventDate')
            event_time = event.get('eventTime')
            onsale_date = event.get('onsaleDate')
            onsale_time = event.get('onsaleTime')
            
            start_datetime_str = None
            if event_date and event_time:
                start_datetime_str = f"{event_date}T{event_time}{time_offset}"
            
            onsale_datetime_str = None
            if onsale_date and onsale_time:
                onsale_datetime_str = f"{onsale_date}T{onsale_time}{time_offset}"
            
            source_data = SourceEvent(
                name=event.get("eventName"),
                event_id=event.get("eventId"),
                description=event_data.get("esText"),
                start_datetime=normalize_datetime(dt=start_datetime_str),
                end_datetime=None,
                venue=venue,
                currency="SEK",
                price_range=list(
                    filter(
                        None, [event_data.get("minPrice"), event_data.get("maxPrice")]
                    )
                ),
                ticket_link=event.get("eventLink"),
                status=STATUSES.get(event.get("eventStatus")),
                sold_out=int(event.get("ticketStock")) > 0,
                date_tickets_sale_start=normalize_datetime(dt=onsale_datetime_str),
                organizer=None,
                tags=None,
                image=next(
                    filter(
                        None,
                        [event_data.get("esPictureBig"), event_data.get("esPicture")],
                    )
                ),
                artists=[
                    artist.get("artistName") for artist in event_data.get("artists")
                ],
                explicit_category = None
            )
            events.append(Event(source="eventim", source_data=source_data))
        return events
