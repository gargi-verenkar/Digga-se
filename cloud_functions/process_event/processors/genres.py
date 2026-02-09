import json

import logging
from sqlalchemy import text
from openai import OpenAI
from pydantic import BaseModel

from database.db_connection import get_db_engine

db = None

open_ai_client = None


def assign_genres(event: dict) -> dict:
    if not event:
        raise ValueError(f"No event to assign genres: {event}")
    genres_candidates = get_genres()
    matched_genres: GenresMatchResponse = match_to_genres(
        candidates=genres_candidates, event=event
    )
    event["genre_ids"] = matched_genres.matched_genre_ids
    event["subgenres"] = matched_genres.matched_sub_genre_names[:2]
    return event


class GenresMatchResponse(BaseModel):
    matched_genre_ids: list[int]
    matched_genre_names: list[str]
    matched_sub_genre_names: list[str]
    reason: str
    input_event_name: str
    input_event_description: str


def match_to_genres(candidates: list[dict], event: dict) -> GenresMatchResponse:
    global open_ai_client
    if not open_ai_client:
        open_ai_client = OpenAI()

    completion = open_ai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[
            {"role": "system", "content": "You are a data classifier."},
            {
                "role": "user",
                "content": f"Given the following list of candidate genres:"
                f"{candidates}"
                f"Assign maximum 0-1 (zero to one) matching main genre that best fits the title, description or other fields for this cultural event, from the list of candidate genres."
                f"You MAY also assign maximum 0-2 (zero to two) sub music genres if that is fitting for the particular music event."
                f"\n"
                f"Input event:"
                f"{event}"
                f"\n",
            },
        ],
        response_format=GenresMatchResponse,
    )
    message = completion.choices[0].message
    if message.parsed:
        response: GenresMatchResponse = message.parsed
        logging.info(
            f"openai response: {json.dumps(response.model_dump(), ensure_ascii=False)}"
        )
        return response
    else:
        logging.error(
            f"Something went wrong when trying to match genres for event: {event}"
        )
        logging.error(message.refusal)
        raise ValueError(
            f"Something went wrong when trying to match genres for event: {event}"
        )


def get_genres() -> list[dict[int, str]]:
    global db
    if not db:
        db = get_db_engine()

    try:
        with db.connect() as conn:
            sql_query = text(
                """
                SELECT id, name
                FROM genres
            """
            )
            result = conn.execute(sql_query)
            themes = result.fetchall()
            genres_list = [dict(row._mapping) for row in themes]
            logging.info(f"Found {len(genres_list)} genres")
            return genres_list

    except Exception as e:
        logging.error(f"Error fetching genres: {e}")
        raise e
