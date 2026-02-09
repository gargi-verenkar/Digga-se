import re
from builtins import list

from raw_events.svenskakyrkan.api import get_events, get_places
from raw_events.fetcher import EventFetcher, normalize_zipcode, normalize_datetime
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class SvenskakyrkanFetcher(EventFetcher):

    titles = "radiokören|orgelmacka|musikal|magnificat|passion|konsert|lunchmusik|orgelmusik|requiem|måndagsmusik|tisdagsmusik|onsdagsmusik|torsdagsmusik|fredagsmusik|lördagsmusik|söndagsmusik"

    def __init__(
        self, gcp_project: str, pubsub_topic: str, ocp_api_key: str, svk_api_key: str
    ) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)
        self.ocp_api_key = ocp_api_key
        self.svk_api_key = svk_api_key

    def get_events(self) -> list[Event]:
        places = {
            place["id"]: place for place in get_places(svk_api_key=self.svk_api_key)
        }
        events = get_events(ocp_api_key=self.ocp_api_key)
        result = [self.to_event(event, places) for event in events]
        return [
            event
            for event in result
            if re.search(pattern=self.titles, string=event.source_data.name.lower())
        ]

    @staticmethod
    def to_event(event_data: dict, places: dict) -> Event:
        venue = None
        place = places.get(event_data.get("place", {}).get("id"))
        if place:
            coordinates = place.get("geolocation").get("geometry").get("coordinates")
            venue = Venue(
                city=place.get("visitingInfo").get("city"),
                address_text=place.get("visitingInfo").get("address"),
                zipcode=normalize_zipcode(place.get("visitingInfo").get("postalCode")),
                name=place.get("name"),
                coordinates=Coordinates(
                    latitude=coordinates[0], longitude=coordinates[1]
                ),
            )
        source_data = SourceEvent(
            name=event_data.get("title"),
            event_id=event_data.get("id"),
            description=event_data.get("description"),
            start_datetime=normalize_datetime(event_data.get("start")),
            end_datetime=normalize_datetime(event_data.get("end")),
            venue=venue,
            currency="SEK",
            price_range=None,
            ticket_link=f"https://www.svenskakyrkan.se/kalender?eventId={event_data.get('id')}",
            status=None,
            sold_out=None,
            date_tickets_sale_start=None,
            organizer=event_data.get("owner").get("name"),
            tags=None,
            image=None,
            artists=None,
            explicit_category = None
        )
        return Event(source="svenskakyrkan", source_data=source_data)
