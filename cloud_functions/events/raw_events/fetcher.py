import abc
import json
import os
import re
from datetime import datetime
import html
import pytz

from bs4 import BeautifulSoup
from dateutil import parser
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from google.cloud import logging as cloud_logging
from google.cloud import pubsub_v1
import logging
from sqlalchemy import text

from database.db_connection import get_db_engine
from raw_events.models import Event, to_dict, to_event, to_json

# Set up Cloud Logging
client = cloud_logging.Client()
client.setup_logging()


class EventFetcher:

    def __init__(self, gcp_project: str, pubsub_topic: str) -> None:
        # Validate input parameters
        if not gcp_project or gcp_project.isspace():
            raise ValueError("Missing GCP project name")
        if not pubsub_topic or pubsub_topic.isspace():
            raise ValueError("Missing Pub/Sub topic name")
        # Initialize properties
        self.gcp_project = gcp_project
        self.pubsub_topic = pubsub_topic
        with open(
            f"{os.path.dirname(__file__)}/../schemas/internal_event_schema.json", "r"
        ) as file:
            self.schema = json.load(file)

    def fetch_events(self):
        # Retrieve events from source system
        source_events = self.get_events()
        logging.info(f"Fetched {len(source_events)} events from the source")
        if not source_events:
            logging.info("There are no events in the source, skipping remaining steps")
            return

        # Filter past events
        upcoming_events = list(
            filter(
                lambda event: not is_past(event.source_data.start_datetime),
                source_events,
            )
        )
        logging.info(
            f"There are {len(upcoming_events)} upcoming events from the source"
        )
        if not upcoming_events:
            logging.info(
                "There are no upcoming events in the source, skipping remaining steps"
            )
            return
        source = upcoming_events[0].source
        existing_events = get_existing_events(source)

        # Find deleted events
        deleted_events = []
        upcoming_events_map = {
            event.source_data.event_id: event
            for event in upcoming_events
            if event.source_data.event_id
        }
        for existing_id, existing_data in existing_events.items():
            if (
                not is_past(existing_data.get("start_datetime"))
                and ("status" in existing_data and existing_data["status"] != "Deleted")
                and not upcoming_events_map.get(existing_id)
            ):
                existing_data["status"] = "Deleted"
                deleted_events.append(to_event(existing_data, source))
        logging.info(f"There are {len(deleted_events)} deleted events from the source")
        # Find new events
        new_events = list(
            filter(
                lambda event: event.source_data.event_id not in existing_events.keys(),
                upcoming_events,
            )
        )
        logging.info(f"There are {len(new_events)} new events")
        # Find changed events
        changed_events = []
        for source_event in upcoming_events:
            existing_event = existing_events.get(source_event.source_data.event_id)
            if existing_event and existing_event != to_dict(source_event.source_data):
                changed_events.append(source_event)
        logging.info(f"There are {len(changed_events)} changed events")

        if not new_events and not changed_events:
            logging.info(
                "There are no new or changed events in the source, skipping remaining steps"
            )
            return

        new_and_changed_events = new_events + changed_events + deleted_events
        logging.info(
            f"There are {len(new_and_changed_events)} remaining out of {len(source_events)} events to proceed"
        )

        # Filter invalid events
        valid_events = list(filter(self.is_valid_event, new_and_changed_events))
        logging.info(
            f"Filtered invalid events: {len(valid_events)} remaining out of {len(new_and_changed_events)}"
        )
        if not valid_events:
            logging.info(
                "There are no valid events in the source, skipping remaining steps"
            )
            return

        # Publish events
        self.publish_events(valid_events)

    @abc.abstractmethod
    def get_events(self) -> list[Event]:
        pass

    def is_valid_event(self, event: Event) -> bool:
        try:
            event_dict = to_dict(event)
            validate(instance=event_dict, schema=self.schema)
            return True
        except ValidationError as error:
            logging.info(f"{error.json_path}: {error.message}")
            return False

    def publish_events(self, events: list[Event]):
        logging.info(
            f"Publish {len(events)} events to {self.gcp_project}/topics/{self.pubsub_topic}"
        )

        # Batch settings for controlling batch behavior
        batch_settings = pubsub_v1.types.BatchSettings(
            max_bytes=1024 * 1024 * 5,  # Maximum bytes of 5MB
            max_latency=5,  # Maximum latency of 0.5 seconds
            max_messages=1000,  # Maximum number of messages
        )

        # Initialize the Publisher client with batch settings
        publisher = pubsub_v1.PublisherClient(batch_settings=batch_settings)
        topic_path = publisher.topic_path(self.gcp_project, self.pubsub_topic)

        futures = []
        success_count = 0
        failure_count = 0

        def get_callback(publish_future, data):
            def callback(publish_future):
                nonlocal success_count, failure_count
                try:
                    # Wait for the result of the publish call.
                    publish_future.result()
                    success_count += 1
                except Exception as ex:
                    logging.error(f"Publishing message {data} threw an Exception {ex}.")
                    failure_count += 1

            return callback

        try:
            for event in events:
                event_json = to_json(event).encode("utf-8")
                publish_future = publisher.publish(topic_path, event_json)
                publish_future.add_done_callback(
                    get_callback(publish_future, event_json)
                )
                futures.append(publish_future)

            # Wait for all futures to resolve before returning.
            for future in futures:
                future.result()
        except Exception as e:
            logging.error(f"Failed to publish events: {e}")
        finally:
            logging.info(
                f"Successfully published {success_count} events. Failed to publish {failure_count} events."
            )


def get_existing_events(event_source: str) -> dict:
    try:
        db = get_db_engine()
        with db.connect() as conn:
            query = """
            SELECT data->'source_data'->>'event_id' AS event_id,
                   data->'source_data' as source_data
            FROM events
            WHERE source = :source
            """
            rows = conn.execute(
                statement=text(query), parameters={"source": event_source}
            ).fetchall()
            existing_events = {
                row._mapping["event_id"]: row._mapping["source_data"] for row in rows
            }
            return existing_events
    except Exception as e:
        logging.error(f"Error fetching existing event IDs: {e}")        
        raise ValueError(f"Error fetching existing event IDs: {e}")


def normalize_zipcode(zipcode: str) -> int or None:
    if not zipcode:
        return None
    zipcode = zipcode.replace(" ", "")
    if not re.match(pattern="^[1-9]{1}[0-9]{4}$", string=zipcode):
        return None
    return int(zipcode)


def normalize_datetime(dt: str, tz: str = None) -> str or None:
    if not dt or dt.isspace():
        return None
    
    # Handle invalid datetime strings that might contain "None" or other invalid formats
    if "None" in dt or dt.startswith("T") or not dt.replace("T", "").replace(":", "").replace("-", "").replace("+", "").replace("Z", "").replace(" ", "").strip():
        return None
    
    try:
        parsed_dt = parser.parse(dt)
        if tz:
            parsed_dt = pytz.timezone(tz).localize(parsed_dt)
        return parsed_dt.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError, parser.ParserError):
        # If parsing fails, return None instead of raising an exception
        return None


def is_past(dt: str) -> bool:
    if not dt:
        return False
    try:
        from dateutil import parser
        # Use dateutil.parser for robust datetime parsing
        parsed_dt = parser.parse(dt)
        # Convert to naive datetime for comparison with datetime.now()
        if parsed_dt.tzinfo is not None:
            parsed_dt = parsed_dt.replace(tzinfo=None)
        return parsed_dt < datetime.now()
    except (ValueError, TypeError):
        # If parsing fails, assume it's not past
        return False
