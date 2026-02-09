import json

import logging
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("digga-se", "sync_to_external")


def publish_to_sync(event: dict):
    logging.info(f"Publish to {topic_path}: {event}")
    future = publisher.publish(topic_path, json.dumps(event).encode("utf-8"))
    future.result()
