import os
import logging
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool  # Changed from QueuePool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_db_engine():
    # Environment variables
    db_instance_connection_name = os.getenv("DB_INSTANCE_CONNECTION_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    if not db_instance_connection_name or not db_user or not db_password or not db_name:
        raise EnvironmentError(
            "Environment variables DB_NAME, DB_USER, DB_PASSWORD and DB_INSTANCE_CONNECTION_NAME must be set"
        )

    # Initialize the Connector
    connector = Connector()

    # Global connection object
    def get_connection():
        logger.info("Connecting to DB via Cloud SQL Connector...")

        try:
            conn = connector.connect(
                instance_connection_string=db_instance_connection_name,
                driver="pg8000",
                user=db_user,
                password=db_password,
                db=db_name,
                ip_type=IPTypes.PUBLIC,
            )
            return conn
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise

    # SQLAlchemy engine with NullPool for serverless environments
    # This prevents "Too many connections" errors by ensuring 
    # connections are closed immediately after use.
    engine = create_engine(
        "postgresql+pg8000://",
        creator=get_connection,
        poolclass=NullPool,  # This is the key fix
    )
    return engine