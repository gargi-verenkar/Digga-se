import json
import logging
from sqlalchemy import text
from openai import OpenAI
from pydantic import BaseModel

from database.db_connection import get_db_engine

db = None

open_ai_client = None


def categorize(event: dict) -> dict:
    if not event:
        raise ValueError(f"No event to categorize: {event}")
    
    category_candidates = get_categories()
    
    category = event.get("source_data", {}).get("explicit_category")

    # If an explicit category wasn't given, ask openAI to figure it out
    if category is None:
        category = match_to_category(candidates=category_candidates, event=event)

    # Get the id, and include flag for the category
    category_data = next((cat for cat in category_candidates if cat.get("name", "").lower() == category.lower()), None)

    if category_data is None:
        errorMessage = f"Could not match category {category} with any of the categories in the DB for event: {event}"
        logging.error(errorMessage)
        raise ValueError(errorMessage)

    event["category_id"] = category_data.get("id")
    event["category_name"] = category_data.get("name")
    event["category_include"] = category_data.get("include")
    return event


def get_categories() -> list[dict]:
    global db
    if not db:
        db = get_db_engine()
    try:
        with db.connect() as conn:
            sql_query = text(
                """
                SELECT id, name, include, definition
                FROM categories
            """
            )
            result = conn.execute(sql_query)
            categories = result.fetchall()
            category_list = [dict(row._mapping) for row in categories]
            return category_list
    except Exception as e:
        logging.error(f"Error fetching categories: {e}")
        raise e

class CategoryMatchResponse(BaseModel):
    matched_category_name: str
    reason: str
    input_event_name: str
    input_event_description: str

def match_to_category(candidates: list[dict], event: dict) -> str:
    global open_ai_client

    category_name_definitions = [
        {"name": cat["name"], "definition": cat["definition"]}
        for cat in candidates
    ]

    if not open_ai_client:
        open_ai_client = OpenAI()
    
    completion = open_ai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[
            {"role": "system", "content": "You are a data classifier."},
            {
                "role": "user",
                "content": f"Given the following list of candidate categories and their definitions:"
                f"{category_name_definitions}"
                f"Find the category from the list where the category and definition best fits the title, description, or other fields for this cultural event. Some of the categories have been supplied with an explicit definition, if the event matches this definition then the event HAS to be given this category."
                f"\n"
                f"Input event:"
                f"{event}"
                f"\n",
            },
        ],
        response_format=CategoryMatchResponse,
    )

    if not completion.choices:
        logging.error(f"AI model did not reply with category choices.")
        raise ValueError(f"AI model did not reply with category choices.")

    message = completion.choices[0].message
    if message.parsed:
        response: CategoryMatchResponse = message.parsed
        logging.info(
            f"openai response: {json.dumps(response.model_dump(), ensure_ascii=False)}"
        )

        return response.matched_category_name
    else:
        logging.error(
            f"Something went wrong when trying to match category for event: {event} with AI"
        )
        logging.error(message.refusal)
        raise ValueError(
            f"Something went wrong when trying to match category for event: {event} with AI"
        )