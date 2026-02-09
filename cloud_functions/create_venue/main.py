import json
import functions_framework
from flask import Request, jsonify, make_response, request
from google.cloud import secretmanager, logging as cloud_logging
from shared.db_connection import get_db_engine
from sqlalchemy import text
import logging

# Set up Cloud Logging
client = cloud_logging.Client()
client.setup_logging()

db = None

# Access Secret Manager
secret_client = secretmanager.SecretManagerServiceClient()
secret_name = "projects/digga-se/secrets/AIRDEV_API_KEY/versions/latest"


def get_secret():
    response = secret_client.access_secret_version(request={"name": secret_name})
    secret_string = response.payload.data.decode("UTF-8")
    return secret_string


@functions_framework.http
def create_venue(request: Request):
    # Verify the HTTP method
    if request.method != "POST":
        return make_response(jsonify({"error": "Method Not Allowed: only POST"}), 405)

    try:
        global db
        if not db:
            db = get_db_engine()

        # Retrieve and verify the secret
        secret_value = get_secret()
        auth_header = request.headers.get(
            "X-Forwarded-Authorization"
        )  # API Gateway moves bearer token from Authorization header to this header
        if not auth_header or not auth_header.startswith("Bearer "):
            logging.warning("Missing or invalid Authorization header.")
            return make_response(jsonify({"error": "Unauthorized"}), 401)

        received_token = auth_header.split("Bearer ")[1]
        if received_token != secret_value:
            logging.warning("Unauthorized access attempt with incorrect Bearer token.")
            return make_response(jsonify({"error": "Unauthorized"}), 401)

        # Get the JSON body from the request
        venue_data = request.get_json()
        logging.info(f"Received venue data: {venue_data}")

        # Validate required fields
        required_fields = ["name", "zipcode", "city", "country_code", "type"]
        missing_fields = [field for field in required_fields if field not in venue_data]

        if missing_fields:
            error_message = f"Missing required fields: {', '.join(missing_fields)}"
            logging.warning(error_message)
            return make_response(jsonify({"error": error_message}), 400)

        # Proceed with the insert operation
        with db.connect() as conn:
            try:
                # Insert the new venue data
                sql_query = text(
                    """
                    INSERT INTO venues (name, search_name, address, zipcode, city, country_code, type)
                    VALUES (:name, :search_name, :address, :zipcode, :city, :country_code, :type)
                    RETURNING id, external_id
                """
                )
                sql_params = {
                    "name": venue_data["name"],
                    "search_name": venue_data.get(
                        "search_name", None
                    ),  # Optional field
                    "address": venue_data.get("address", None),  # Optional field
                    "zipcode": venue_data["zipcode"],
                    "city": venue_data["city"],
                    "country_code": venue_data["country_code"],
                    "type": venue_data["type"],
                }
                logging.info(
                    f"Executing SQL query: {sql_query} with params: {sql_params}"
                )
                result = conn.execute(sql_query, sql_params)
                inserted_row = result.fetchone()

                # Ensure conn.commit() is called after a successful insert
                conn.commit()

                if inserted_row:
                    # Use the _mapping attribute to convert the RowProxy to a dictionary
                    inserted_row_dict = dict(inserted_row._mapping)
                    logging.info(
                        f"Created new venue with ID {inserted_row_dict['id']} in the database."
                    )
                    return (
                        jsonify({"status": "success", "id": inserted_row_dict["id"]}),
                        201,
                    )
                else:
                    logging.error("Failed to create new venue.")
                    return jsonify({"error": "Failed to create venue."}), 500

            except Exception as e:
                logging.error(f"Error during create operation: {e}")
                conn.rollback()
                raise e

    except Exception as e:
        logging.error(f"Error handling the request: {e}")
        return jsonify({"error": str(e)}), 500
