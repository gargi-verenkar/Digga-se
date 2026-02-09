import json

from sqlalchemy import text
import logging

from database.db_connection import get_db_engine

db = None


def read_event(source: str, source_event_id: str) -> dict or None:
    if not source or not source_event_id:
        return None
    try:
        global db
        if not db:
            db = get_db_engine()

        with db.connect() as conn:
            query = """
            SELECT data
            FROM events
            WHERE source = :source
              AND data->'source_data'->>'event_id' = :source_event_id
            """
            event = conn.execute(
                statement=text(query),
                parameters={"source": source, "source_event_id": source_event_id},
            ).fetchone()
            if event:
                return dict(event._mapping["data"])
            else:
                return None
    except Exception as e:
        logging.error(f"Error fetching event: {e}")
        raise e


def write_event(event: dict) -> dict:
    try:
        global db
        if not db:
            db = get_db_engine()

        with db.connect() as conn:
            try:
                sql_query = text(
                    """
                    INSERT INTO events (data, venue_id, source)
                    VALUES (:data, :venue_id, :source)
                    ON CONFLICT ((data->'source_data'->>'event_id'), source)
                    DO UPDATE SET
                        data = EXCLUDED.data,
                        venue_id = EXCLUDED.venue_id
                    RETURNING id, external_id
                """
                )
                sql_params = {
                    "data": json.dumps(event),
                    "venue_id": event.get("venue_id", None),
                    "source": event["source"],
                }
                
                row = conn.execute(sql_query, sql_params).fetchone()
                query_result = row._mapping
                event["id"] = query_result["id"]
                event["external_id"] = query_result["external_id"]
                conn.commit()  # Ensure commit is called before returning
                logging.info(
                    f"Event with external ID {event['external_id']} upserted into database."
                )
                return event
            except Exception as insert_e:
                logging.error(f"Error during upsert operation: {insert_e}")
                conn.rollback()
                raise insert_e
    except Exception as e:
        logging.error(f"Error writing event to database: {e}")
        raise e
