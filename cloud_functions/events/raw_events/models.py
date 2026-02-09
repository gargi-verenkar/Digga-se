import json


class Coordinates:

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude


class Venue:

    def __init__(
        self,
        city: str,
        address_text: str,
        zipcode: int or None,
        name: str,
        coordinates: Coordinates or None,
    ):
        self.city = city
        self.address_text = address_text
        self.zipcode = zipcode
        self.name = name
        self.coordinates = coordinates


class SourceEvent:

    def __init__(
        self,
        name: str,
        event_id: str,
        description: str or None,
        start_datetime: str,
        end_datetime: str or None,
        venue: Venue,
        currency: str or None,
        price_range: list or None,
        ticket_link: str or None,
        status: str or None,
        sold_out: bool or None,
        date_tickets_sale_start: str or None,
        organizer: str or None,
        tags: list[str] or None,
        image: str or None,
        artists: list[str] or None,
        explicit_category: str or None,
    ) -> None:
        self.name = name
        self.event_id = event_id
        self.description = description
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.venue = venue
        self.currency = currency
        self.price_range = price_range
        self.ticket_link = ticket_link
        self.status = status
        self.sold_out = sold_out
        self.date_tickets_sale_start = date_tickets_sale_start
        self.organizer = organizer
        self.tags = tags
        self.image = image
        self.artists = artists
        self.explicit_category = explicit_category


class Event:

    def __init__(
        self,
        source: str,
        source_data: SourceEvent,
        category_id: int = None,
        theme_ids: list[int] = None,
        genre_ids: list[int] = None,
        subgenres: list[str] = None,
        venue_id: int = None,
    ):
        self.source = source
        self.source_data = source_data
        self.category_id = category_id
        self.theme_ids = theme_ids
        self.genre_ids = genre_ids
        self.subgenres = subgenres
        self.venue_id = venue_id


def to_dict(model: object):
    return json.loads(to_json(model))


def to_json(model: object):
    return json.dumps(
        obj=model, default=lambda x: {k: v for k, v in x.__dict__.items() if v}
    )


def to_event(source_data: dict, source: str) -> Event:
    return Event(source_data=to_source_event(source_data), source=source)


def to_source_event(source_data: dict) -> SourceEvent:
    return SourceEvent(
        name=source_data.get("name"),
        event_id=source_data.get("event_id"),
        description=source_data.get("description"),
        start_datetime=source_data.get("start_datetime"),
        end_datetime=source_data.get("end_datetime"),
        venue=to_venue(source_data.get("venue")),
        currency=source_data.get("currency"),
        price_range=source_data.get("price_range"),
        ticket_link=source_data.get("ticket_link"),
        status=source_data.get("status"),
        sold_out=source_data.get("sold_out"),
        date_tickets_sale_start=source_data.get("date_tickets_sale_start"),
        organizer=source_data.get("organizer"),
        tags=source_data.get("tags"),
        image=source_data.get("image"),
        artists=source_data.get("artists"),
        explicit_category=source_data.get("explicit_category"),
    )


def to_venue(venue: dict) -> Venue:
    return Venue(
        name=venue.get("name"),
        city=venue.get("city"),
        address_text=venue.get("address_text"),
        zipcode=venue.get("zipcode"),
        coordinates=(
            to_coordinates(venue.get("coordinates"))
            if venue.get("coordinates")
            else None
        ),
    )


def to_coordinates(coordinates: dict) -> Coordinates:
    return Coordinates(
        latitude=coordinates.get("latitude") if coordinates.get("latitude") else None,
        longitude=(
            coordinates.get("longitude") if coordinates.get("longitude") else None
        ),
    )
