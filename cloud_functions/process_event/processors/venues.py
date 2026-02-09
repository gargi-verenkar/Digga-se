import json
import re
from typing import Optional

import logging
from sqlalchemy import text
from openai import OpenAI
from pydantic import BaseModel

from database.db_connection import get_db_engine

db = None

open_ai_client = None


def connect_to_venue(event: dict) -> dict:
    if not event:
        raise ValueError(f"No event for venue connect: {event}")
    venue_candidates = get_venues()
    event_venue = event.get("source_data", {}).get("venue", {})
    event_organizer = event.get("source_data", {}).get("organizer", "")
    if (
        venue_id := match_exact(candidates=venue_candidates, source_venue=event_venue)
    ) or (
        venue_id := match_on_organizer(
            candidates=venue_candidates, event_organizer=event_organizer
        )
    ):
        event["venue_id"] = venue_id
    else:
        raise ValueError(f"Event could not be mapped to a venue.")
    return event


def get_venues(zipcode: Optional[int] = None) -> list[dict]:
    global db
    if not db:
        db = get_db_engine()

    try:
        with db.connect() as conn:
            if zipcode is not None:
                # Prepare the SQL query to fetch venues by the given zipcode
                sql_query = text(
                    """
                    SELECT id, name, city, address, zipcode, default_organizer
                    FROM venues
                    WHERE zipcode = :zipcode
                """
                )
                params = {"zipcode": zipcode}
                logging.info(
                    f"Executing SQL query to fetch venues with zipcode: {zipcode}"
                )
            else:
                # Prepare the SQL query to fetch all venues
                sql_query = text(
                    """
                    SELECT id, name, city, address, zipcode, default_organizer
                    FROM venues
                """
                )
                params = {}
                logging.info("Executing SQL query to fetch all venues")

            result = conn.execute(sql_query, params)

            # Fetch all rows that match the query
            venues = result.fetchall()

            # Convert the result into a list of dictionaries
            venues_list = [dict(row._mapping) for row in venues]

            logging.info(f"Found {len(venues_list)} venues")
            return venues_list

    except Exception as e:
        logging.error(f"Error fetching venues: {e}")
        raise e


def match_exact(candidates: list[dict], source_venue: dict) -> int or None:
    # Return None if source venue doesn't have name or city values for exact match
    if not source_venue.get("name") or not source_venue.get("city"):
        return None

    for candidate in candidates:
        if is_equal(source_venue.get("name"), candidate.get("name")) and is_equal(
            source_venue.get("city"), candidate.get("city")
        ):
            return candidate.get("id")
    return None


def is_equal(value1: str, value2: str):
    value1 = normalize(value1)
    value2 = normalize(value2)
    if value1 and value2:
        return value1 == value2
    return False


def normalize(value: str):
    if value:
        value = value.lower()
        value = value.replace("é", " e ")
        value = value.replace("&", " och ")
        value = re.sub(r"[^\w\s]", "", value)  # Remove special characters
        value = " ".join(value.split())  # Remove extra spaces
    return value if value else None


def match_on_organizer(candidates: list[dict], event_organizer: str) -> int or None:
    if not event_organizer:
        return None

    for candidate in candidates:
        if is_equal(candidate.get("default_organizer", ""), event_organizer):
            return candidate.get("id")
    return None


class MatchedVenue(BaseModel):
    id: int
    name: str
    address: str
    zipcode: int


class InputVenue(BaseModel):
    name: str
    address_text: str
    zipcode: int


class VenueMatchResponse(BaseModel):
    matched_venue_id: Optional[int]
    matched_venue: Optional[MatchedVenue]
    reason: str
    input_venue: InputVenue
