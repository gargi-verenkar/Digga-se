import json

import logging
from sqlalchemy import text
from openai import OpenAI
from pydantic import BaseModel

from database.db_connection import get_db_engine

db = None

open_ai_client = None


def assign_themes(event: dict) -> dict:
    if not event:
        raise ValueError(f"No event to assign themes: {event}")
    themes_candidates = get_themes()
    matched_theme_ids = match_to_themes(candidates=themes_candidates, event=event)
    event["theme_ids"] = matched_theme_ids
    return event


class GenresMatchResponse(BaseModel):
    matched_genre_ids: list[int]
    matched_genre_names: list[str]
    matched_sub_genre_names: list[str]
    reason: str
    input_event_name: str
    input_event_description: str


class ThemesMatchResponse(BaseModel):
    matched_themes_ids: list[int]
    matched_themes_names: list[str]
    reason: str
    input_event_name: str
    input_event_description: str


def match_to_themes(candidates: list[dict], event: dict) -> list[int]:
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
                "content": f"Given the following list of candidate themes and their description:"
                f"{candidates}"
                f"Carefully review the event details and assign a maximum of one (0-1) main theme. Only assign a theme if the event explicitly matches the description of that theme. If the event does not clearly and closely align with any theme description, do not assign a theme."
                f"\n"
                f"Input event:"
                f"{event}"
                f"\n",
            },
        ],
        response_format=ThemesMatchResponse,
    )
    message = completion.choices[0].message
    if message.parsed:
        response: ThemesMatchResponse = message.parsed
        logging.info(
            f"openai response: {json.dumps(response.model_dump(), ensure_ascii=False)}"
        )
        return response.matched_themes_ids
    else:
        logging.error(
            f"Something went wrong when trying to match themes for event: {event}"
        )
        logging.error(message.refusal)
        raise ValueError(
            f"Something went wrong when trying to match themes for event: {event}"
        )


def get_themes() -> list[dict[int, str]]:
    global db
    if not db:
        db = get_db_engine()

    try:
        with db.connect() as conn:
            sql_query = text(
                """
                SELECT id, name, description
                FROM themes
            """
            )
            result = conn.execute(sql_query)
            themes = result.fetchall()
            themes_list = [dict(row._mapping) for row in themes]
            logging.info(f"Found {len(themes_list)} categories")
            return themes_list

    except Exception as e:
        logging.error(f"Error fetching themes: {e}")
        raise e
