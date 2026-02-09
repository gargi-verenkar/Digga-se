import base64
import json
import logging

import functions_framework
from google.cloud import logging as cloud_logging
from cloudevents.http import CloudEvent

from processors.categories import categorize
from processors.genres import assign_genres
from processors.themes import assign_themes
from processors.venues import connect_to_venue
from datastore.db import read_event, write_event
from datastore.pubsub import publish_to_sync


# Set up Cloud Logging
client = cloud_logging.Client()
client.setup_logging()


@functions_framework.cloud_event
def process_event(cloud_event: CloudEvent) -> None:
    message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
    logging.info(f"Received message={message}")

    event = json.loads(message)

    existing_event = read_event(
        source=event.get("source"),
        source_event_id=event.get("source_data").get("event_id"),
    )
    if existing_event:
        logging.info(f"The event was processed earlier, use previous results: {existing_event}")
        for field in [
            "category_id",
            "category_name",
            "category_include",
            "venue_id",
            "theme_ids",
            "genre_ids",
            "subgenres",
        ]:
            if existing_event.get(field) is not None:
                event[field] = existing_event.get(field)
    else:
        event = categorize(event)
        logging.info(f"Categorized event={event}")
        if event["category_include"]:
            # Connect to venue
            try:
                event = connect_to_venue(event)
                logging.info(f"Connected to venue: {event}")
            except:
                logging.warning(f"Cannot connect venue for the event: {event}", exc_info=True)
            # Assign themes
            try:
                event = assign_themes(event)
                logging.info(f"Assigned themes: {event}")
            except:
                logging.warning(f"Cannot assign themes for the event: {event}", exc_info=True)
            # Assign genres
            if event["category_name"] == "Concert" or event["category_name"] == "Club":
                try:
                    event = assign_genres(event)
                    logging.info(f"Assigned genres: {event}")
                except:
                    logging.warning(f"Cannot assign genres for the event: {event}", exc_info=True)

    # Write event to database
    event = write_event(event)
    logging.info(f"Event saved in database: {event}")
    # Publish to web app
    if event["category_include"]:
        publish_to_sync(event)
        logging.info(f"Event published to Pub/Sub topic {event}")
    else:
        logging.info(f"There is no category, skip event publishing to Pub/Sub topic {event}")
