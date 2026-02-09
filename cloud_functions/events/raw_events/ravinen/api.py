import requests
from datetime import datetime, timedelta

import json


def get_events() -> list[dict]:
    now = datetime.now()
    from_date = now.strftime("%Y-%m-%dT%H:%M:%S")
    one_year_later = now + timedelta(days=365)
    until_date = one_year_later.strftime("%Y-%m-%dT%H:%M:%S")

    # Define the query string
    query = """
    query ArticleQuery(
      $currency: String
      $culture: String
      $posId: Int
      $from: DateTime
      $until: DateTime
    ) {
      allotments(
        currency: $currency
        culture: $culture
        posId: $posId
        from: $from
        until: $until
      ) {
        id
        description
        imageFileName
        translation {
          culture
          name
          description
        }
        occasions {
          time
          remaining
        }
        articles {
          id
          plu
          name
          priceInclVat
          imageFilename
          price {
            amountInclVat
          }
          translation {
            culture
            name
            description
          }
        }
      }
    }
    """

    # Define the variables
    variables = {
        "currency": "SEK",
        "culture": "sv-SE",
        "posId": 12,
        "from": from_date,
        "until": until_date
    }

    headers = {
        "Content-Type": "application/json",
        "GraphQL-Require-Preflight": "true"
    }
    json={"query": query, "variables": variables}
    response = requests.post(
        "https://norrviken.entryevent.se/shopapi/graphql",
        json=json,
        headers=headers,
    )
    response.raise_for_status()

    return response.json().get("data", {}).get("allotments", [])
