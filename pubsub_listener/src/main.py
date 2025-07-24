import logging
import json
from google.cloud import pubsub_v1
from google.oauth2 import service_account
import subprocess
import os
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

project_id = os.environ.get("PROJECT_ID")
if not project_id:
    raise ValueError("PROJECT_ID environment variable is not set.")

subscription_id = os.environ.get("SUBSCRIPTION_ID")
if not subscription_id:
    raise ValueError("SUBSCRIPTION_ID environment variable is not set.")

creds_filepath = os.environ.get("CREDS_FILEPATH")
if not creds_filepath:
    raise ValueError("CREDS_FILEPATH environment variable is not set.")
if not os.path.exists(creds_filepath):
    raise FileNotFoundError(f"Credentials file not found: {creds_filepath}")

# Load credentials from the specified file
logger.info(f"Loading credentials from {creds_filepath}")
creds = service_account.Credentials.from_service_account_file(creds_filepath)


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    logger.info(f"Received {message}.")
    data = json.loads(message.data.decode("utf-8"))

    action = data.get("action", "")
    if not action:
        logger.error("No action found in the message.")
        message.ack()
        return
    try:
        logger.info(f"Processing action: {action}")
        response = requests.post(
            f"http://homelab_api:8000/{action}",
            headers={"Content-Type": "application/json"},
            json={
                "source_ip": data.get("source_ip", ""),
                "user": data.get("user", {}),
                "params": data.get("params", {}),
            },
        )
        response.raise_for_status()
        logger.info(f"API response: {response.text}")
    except requests.RequestException as e:
        logger.error(f"Failed to call API: {e}")
    finally:
        message.ack()


def main():
    logging.basicConfig(level=logging.DEBUG)

    subscriber = pubsub_v1.SubscriberClient(credentials=creds)
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    logger.info(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            streaming_pull_future.result()
        except Exception as e:
            logger.info(f"Streaming pull future encountered an error: {e}")
            streaming_pull_future.cancel()


if __name__ == "__main__":
    main()
