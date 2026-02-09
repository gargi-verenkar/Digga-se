import json
import functions_framework
from flask import Request, jsonify, make_response
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
def update_venue(request: Request):
    # Verify the HTTP method
    if request.method != "PATCH":
        return make_response(jsonify({"error": "Method Not Allowed: PATCH only"}), 405)

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
            return make_response(
                jsonify({"error": "Unauthorized call to Update venue"}), 401
            )

        received_token = auth_header.split("Bearer ")[1]
        if received_token != secret_value:
            logging.warning("Unauthorized access attempt with incorrect Bearer token.")
            return make_response(
                jsonify({"error": "Unauthorized call to Update venue"}), 401
            )

        # Extract the venue ID from the URL path
        path_parts = request.path.split("/")
        if len(path_parts) < 3 or not path_parts[-1]:
            return make_response(
                jsonify({"error": f"Invalid URL format: {request.path}"}), 400
            )

        venue_id = path_parts[-1]
        logging.info(f"Updating venue with ID: {venue_id}")

        # Get the JSON body from the request
        update_data = request.get_json()
        logging.info(f"Received update data: {update_data}")

        with db.connect() as conn:
            try:
                # Dynamically build the SQL query based on the fields provided in update_data
                set_clauses = []
                sql_params = {"external_id": venue_id}
                for key, value in update_data.items():
                    set_clauses.append(f"{key} = :{key}")
                    sql_params[key] = value

                if not set_clauses:
                    return make_response(
                        jsonify({"error": "No valid fields provided for update"}), 400
                    )

                sql_query = text(
                    f"""
                    UPDATE venues
                    SET {', '.join(set_clauses)}
                    WHERE external_id = :external_id
                    RETURNING id, external_id
                """
                )

                logging.info(
                    f"Executing SQL query: {sql_query} with params: {sql_params}"
                )
                result = conn.execute(sql_query, sql_params)
                updated_row = result.fetchone()
                conn.commit()

                if updated_row:
                    # Use the _mapping attribute to access the row as a dictionary
                    updated_row_dict = updated_row._mapping
                    logging.info(
                        f"Updated venue with external ID {updated_row_dict['external_id']} in the database."
                    )
                    return (
                        jsonify(
                            {"status": "success", "id": updated_row_dict["external_id"]}
                        ),
                        200,
                    )
                else:
                    logging.error("Failed to update venue.")
                    return jsonify({"error": "Venue not found."}), 404

            except Exception as e:
                logging.error(f"Error during update operation: {e}")
                conn.rollback()
                raise e

    except Exception as e:
        logging.error(f"Error handling the request: {e}")
        return jsonify({"error": str(e)}), 500
