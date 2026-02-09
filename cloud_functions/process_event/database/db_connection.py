import os
import logging
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Explicitly set the logging level to INFO


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
        logger.info("connecting to db...")

        try:
            logger.info(
                f"Instance: {db_instance_connection_name}, User: {db_user}, DB: {db_name}"
            )
            global_conn = connector.connect(
                instance_connection_string=db_instance_connection_name,
                driver="pg8000",
                user=db_user,
                password=db_password,
                db=db_name,
                ip_type=IPTypes.PUBLIC,
            )
            logger.info("DB connection established successfully")
            return global_conn
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            logger.info(f"Error connecting to the database: {e}")
            raise

    # SQLAlchemy engine with connection pool
    engine = create_engine(
        "postgresql+pg8000://",
        creator=get_connection,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )
    return engine
