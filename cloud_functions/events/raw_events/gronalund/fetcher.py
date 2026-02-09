import itertools
import json
from builtins import list

from raw_events.gronalund.api import get_events, get_event_details
from raw_events.fetcher import EventFetcher, normalize_datetime
from raw_events.models import Event, SourceEvent, Venue, Coordinates


class GronaLundFetcher(EventFetcher):

    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        super().__init__(gcp_project=gcp_project, pubsub_topic=pubsub_topic)

    def get_events(self) -> list[Event]:
        events = get_events()
        event_details = get_event_details()
        event_shows = [self.to_event(event, event_details) for event in events]
        return list(itertools.chain(*event_shows))

    @staticmethod
    def to_event(event_data: dict, event_details: dict) -> list[Event]:
        venue = Venue(
            city="Stockholm",
            address_text="Lilla Allmänna Gränd",
            zipcode=11521,
            name="Gröna Lund Stora Scen",
            coordinates=Coordinates(
                latitude=59.32320390823333, longitude=18.097074101844154
            ),
        )

        result = []
        for show in event_data.get("events"):
            external_entry_id = (show.get("externalEntry") or {}).get("externalEntryId", "")

            details = None
            if external_entry_id:
                details = event_details.get(external_entry_id)

            source_data = SourceEvent(
                name=show.get("title"),
                event_id=show.get("id") if show.get("id") else None,
                description=(
                    GronaLundFetcher.get_description_from_details(details)
                    if details else None
                ),
                start_datetime=normalize_datetime(show.get("startDateAndTime"), "CET"),
                end_datetime=normalize_datetime(show.get("endDateAndTime"), "CET"),
                venue=venue,
                currency=None,
                price_range=None,
                ticket_link=(
                    GronaLundFetcher.get_link_from_details(details)
                    if details else None
                ),
                status="Cancelled" if show.get("cancelled") else "Active",
                sold_out=False,
                date_tickets_sale_start=None,
                organizer=None,
                tags=None,
                image=(
                    f"https://prs-cdp-prod-webapiproxy.azurewebsites.net/api/glt/show/{external_entry_id}/image"
                    if external_entry_id else None
                ),
                artists=None,
                explicit_category = None
            )
            result.append(Event(source="gronalund", source_data=source_data))
        return result

    @staticmethod
    def get_description_from_details(details: dict) -> str or None:
        if not details:
            return None
        preamble = details.get("preamble", {})
        if not preamble:
            return None
        result = preamble.get("preamble", "") + "\n\n"
        content = details.get("content")
        if not content:
            return result
        contents = (
            json.loads(content.get("raw", ""))
            .get("content", [{}])[0]
            .get("content", [])
        )
        for content in contents:
            result += content.get("value", "")
        return result

    @staticmethod
    def get_link_from_details(details: dict) -> str or None:
        if not details:
            return None
        slug = details.get("pageLink", {}).get("slug", "")
        if not slug:
            return None
        return "https://www.gronalund.com" + slug
