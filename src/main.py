import logging
import json
from google.cloud import pubsub_v1
from google.oauth2 import service_account
import subprocess
import os

project_id = os.environ.get("PROJECT_ID")
if not project_id:
    raise ValueError("PROJECT_ID environment variable is not set.")

subscription_id = os.environ.get("SUBSCRIPTION_ID")
if not subscription_id:
    raise ValueError("SUBSCRIPTION_ID environment variable is not set.")

host = os.environ.get("MIKROTIK_HOST")
if not host:
    raise ValueError("MIKROTIK_HOST environment variable is not set.")

address_list = os.environ.get("ADDRESS_LIST")
if not address_list:
    raise ValueError("ADDRESS_LIST environment variable is not set.")

ip_ttl = os.environ.get("IP_TTL")
if not ip_ttl:
    raise ValueError("IP_TTL environment variable is not set.")

creds_filepath = os.environ.get("CREDS_FILEPATH")
if not creds_filepath:
    raise ValueError("CREDS_FILEPATH environment variable is not set.")
if not os.path.exists(creds_filepath):
    raise FileNotFoundError(f"Credentials file not found: {creds_filepath}")

# Load credentials from the specified file
logging.info(f"Loading credentials from {creds_filepath}")
creds = service_account.Credentials.from_service_account_file(creds_filepath)


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    logging.info(f"Received {message}.")
    data = json.loads(message.data.decode("utf-8"))

    address = data.get("ip")
    user = data.get("user")
    logging.info(
        f"Adding {address} for user {user.get('email')} to Mikrotik whitelist."
    )
    if not address:
        logging.info("No IP address found in the message.")
        message.ack()
        return

    cmd = (
        f'ssh {host} "/ip/firewall/address-list/add list={address_list} timeout={ip_ttl} address={address} dynamic=yes" > /dev/null || '
        f'ssh {host} "/ip/firewall/address-list/set [find list={address_list} and address={address}] timeout={ip_ttl}"'
    )
    try:
        subprocess.run(cmd, shell=True, check=True)
        logging.info(f"Added {address} to Mikrotik whitelist.")
    except subprocess.CalledProcessError as e:
        logging.info(f"Failed to add {address}: {e}")
    message.ack()


def main():
    logging.basicConfig(level=logging.INFO)
    subscriber = pubsub_v1.SubscriberClient(credentials=creds)
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    logging.info(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            streaming_pull_future.result()
        except Exception as e:
            logging.info(f"Streaming pull future encountered an error: {e}")
            streaming_pull_future.cancel()


if __name__ == "__main__":
    main()
