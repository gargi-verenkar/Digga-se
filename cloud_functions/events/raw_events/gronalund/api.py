import json

import requests


def get_events() -> list[dict]:
    response = requests.get(
        url="https://prs-cdp-prod-webapiproxy.azurewebsites.net/api/glt/Schedule/v2?scheduleTypes=Event"
    )
    response.raise_for_status()
    data = json.loads(response.content)
    return data.get("response")


def get_event_details() -> dict:
    response = requests.get(
        url="https://www.gronalund.com/page-data/konserter/page-data.json"
    )
    response.raise_for_status()
    blocks = (
        json.loads(response.content)
        .get("result", {})
        .get("data", {})
        .get("contentfulContentPage", {})
        .get("blocks", [])
    )
    content_block = _find_with_contentful_id("2EYwHehoFIn7MMxFGxgjhb", blocks)
    koncert_block = _find_with_contentful_id(
        "2UXENHtEp5gTeM4cymjGTq", content_block.get("blocks", [])
    )
    koncert_block_lists = koncert_block.get("lists", [])
    if not koncert_block_lists:
        return {}
    list_of_koncerts = koncert_block_lists[0].get("listObjects", [])
    if not list_of_koncerts:
        return {}
    return {koncert.get("contentful_id"): koncert for koncert in list_of_koncerts}


def _find_with_contentful_id(contentful_id: str, blocks: list[dict]) -> dict:
    for block in blocks:
        if block.get("contentful_id") == contentful_id:
            return block
    return {}
