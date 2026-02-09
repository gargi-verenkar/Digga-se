import base64
import json
import os

import functions_framework
import requests
import logging

from cloudevents.http import CloudEvent
from jsonschema import validate, ValidationError

from google.cloud import logging as cloud_logging
from sqlalchemy import text

from database.db_connection import get_db_engine

# Set up Cloud Logging
client = cloud_logging.Client()
client.setup_logging()

db = None


@functions_framework.cloud_event
def push_to_bubble(cloud_event: CloudEvent) -> None:
    message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
    logging.info(f"message={message}")

    event = json.loads(message)
    logging.info(f"event={event}")

    external_format = to_external_format(event)
    if not is_valid_event(external_format):
        raise ValueError("Event is not valid")

    endpoint_url = os.getenv("ENDPOINT_URL")
    token = os.getenv("TOKEN")
    logging.info(f"Sending request to {endpoint_url}")
    response = requests.post(
        endpoint_url,
        json=external_format,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()
    response_object = response.json().get("response", {})
    logging.info(f"Response from {endpoint_url}: {response_object}")
    if response_object.get("message") not in [
        "Event has been created",
        "Event has been updated",
    ]:
        raise RuntimeError(response_object.get("message"))


def to_external_format(event):
    source_data = event["source_data"]

    transformed_event = {
        "event": {
            "id": (
                str(event.get("external_id"))
                if event.get("external_id") is not None
                else None
            ),
            "category_id": (
                str(event.get("category_id"))
                if event.get("category_id") is not None
                else None
            ),
            "startDateTime": source_data.get("start_datetime"),
            "endDateTime": source_data.get("end_datetime"),
            "name": source_data.get("name"),
            "venueId": (
                str(event.get("venue_id"))
                if event.get("venue_id") is not None
                else None
            ),
            "soldOut": source_data.get("sold_out"),
            "dateTicketsSaleStart": source_data.get("date_tickets_sale_start"),
            "ticketLink": source_data.get("ticket_link"),
        },
        "_metadata": {},
    }

    venue_from_db = get_venue(event.get("venue_id"))
    if venue_from_db:
        transformed_event["_metadata"]["venue"] = venue_from_db
        # Add geolocation if coordinates exist
        if (
            "coordinates" in source_data["venue"]
            and source_data["venue"]["coordinates"] is not None
        ):
            transformed_event["_metadata"]["venue"]["geolocation"] = {
                "latitude": source_data["venue"]["coordinates"]["latitude"],
                "longitude": source_data["venue"]["coordinates"]["longitude"],
            }
    else:
        transformed_event["_metadata"]["venue_hint"] = to_venue_hint(
            source_data["venue"]
        )

    # Add optional fields to event if they are not empty
    for field in ["theme_ids", "genre_ids", "subgenres"]:
        value = event.get(field)
        if value is not None:
            transformed_event["event"][field] = list(map(str, value))

    for field in [
        "description",
        "image",
        "artists",
        "organizer",
        "currency",
        "price_range",
        "status",
    ]:
        value = source_data.get(field)
        if value is not None:
            transformed_event["event"][field] = value

    # Remove None values in venue metadata
    if "venue" in transformed_event["_metadata"]:
        venue_metadata = transformed_event["_metadata"]["venue"]
        venue_metadata = {k: v for k, v in venue_metadata.items() if v is not None}
        transformed_event["_metadata"]["venue"] = venue_metadata

    # Remove None values in event data
    event_metadata = transformed_event["event"]
    event_metadata = {k: v for k, v in event_metadata.items() if v is not None}
    transformed_event["event"] = event_metadata

    return {"$schema": "events_schema.json", "data": transformed_event}


def is_valid_event(event):
    with open("events_schema.json", "r") as file:
        schema = json.load(file)
        try:
            logging.info(f"Validating event: \n {json.dumps(event, indent=4)}")
            validate(instance=event, schema=schema)
            return True
        except ValidationError as e:
            logging.error(f"Event validation error for event {event}: {e.message}")
            return False


def to_venue_hint(venue: dict) -> str:
    name = venue.get("name")
    address = venue.get("address_text")
    zipcode = str(venue["zipcode"]) if venue.get("zipcode") is not None else None
    city = venue.get("city")

    coordinates = venue.get("coordinates")
    if isinstance(coordinates, dict):
        coordinates = f"{coordinates.get('latitude')}, {coordinates.get('longitude')}"

    parts = [name]
    address_parts = []
    if address:
        address_parts.append(address)
    if zipcode and city:
        address_parts.append(f"{zipcode} {city}")
    elif zipcode:
        address_parts.append(zipcode)
    elif city:
        address_parts.append(city)
    if address_parts:
        parts.append(", ".join(address_parts))
    if coordinates:
        parts.append(f"({coordinates})")

    return ", ".join(parts)


def get_venue(venue_id: str or None) -> dict or None:
    if venue_id is None:
        return None

    global db
    if not db:
        db = get_db_engine()

    try:
        with db.connect() as conn:
            sql_query = text(
                """
                SELECT external_id::text as id, name, search_name, address, zipcode, country_code, city, type::integer as type
                FROM venues
                WHERE id = :venue_id
            """
            )
            result = conn.execute(sql_query, {"venue_id": venue_id})
            venue = result.fetchone()
            if venue:
                return dict(
                    venue._mapping
                )  # Return the row as a dictionary-like mapping
            else:
                return None  # Return None if no venue is found
    except Exception as e:
        logging.error(f"Error fetching venues: {e}")
        raise e
