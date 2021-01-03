import os
import sys
from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from google.oauth2 import service_account
script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')
credentials_path = os.path.join(script_dir, '../confidential/workerkey.json')
timeout = 5.0
credentials = service_account.Credentials.from_service_account_file(credentials_path)
subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
project_id = 'principal-fact-300509'
subscription_id = 'listener'
subscription_path = subscriber.subscription_path(project_id, subscription_id)
print(subscription_path)

def callback(message):
    print(f"Received {message}.")
    message.ack()


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")
with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        # timeout=timeout
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()