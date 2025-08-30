"""Option 1"""

import time

from sseclient import SSEClient


def stream_thoughts_client(url, max_retries=2):
    """
    Python client that mimics JavaScript EventSource behavior
    for listening to SSE streams from your Flask endpoint.
    """
    retry_count = 0

    while retry_count <= max_retries:
        try:
            # Equivalent to: new EventSource('/api/stream-thoughts')
            client = SSEClient(url)

            # Reset retry count on successful connection
            retry_count = 0

            # Equivalent to: eventSource.onmessage
            for event in client.events():
                if event.data:
                    display_status(event.data)  # Update with event data

        except Exception as e:
            # Equivalent to: eventSource.onerror
            print(f"SSE connection error: {e}")
            retry_count += 1

            if retry_count > max_retries:
                print("Max retries exceeded. Giving up.")
                break

            # Exponential backoff: wait 1s, then 2s, then 4s, etc.
            backoff_time = 2 ** (retry_count - 1)
            print(
                f"Retrying in {backoff_time} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(backoff_time)


def display_status(data):
    """
    Equivalent to the JS displayStatus function.
    Process the incoming SSE data here.
    """
    print(f"STATUS: {data}")
    # Add your logic to handle different status messages
    # if "Failed" in data:
    #     handle_failure()
    # elif "Success" in data:
    #     handle_success()


# Example usage
if __name__ == "__main__":
    STREAM_URL = "http://localhost:5000/api/stream-thoughts"
    stream_thoughts_client(STREAM_URL)

"""Option 2"""

import time

import requests


def stream_thoughts_client(url, max_retries=2):
    retry_count = 0

    while retry_count <= max_retries:
        try:
            response = requests.get(url, stream=True, timeout=None)
            response.raise_for_status()

            retry_count = 0

            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data:"):
                    data = line[5:].strip()
                    display_status(data)

        except requests.exceptions.RequestException as e:
            print(f"SSE connection error: {e}")
            retry_count += 1

            if retry_count > max_retries:
                break

            backoff_time = 2 ** (retry_count - 1)
            time.sleep(backoff_time)


# display_status function remains the same

import time

import requests


def stream_thoughts():
    retries = 0
    max_retries = 2
    base_delay = 1  # seconds

    while retries <= max_retries:
        try:
            response = requests.get(
                "http://localhost:5000/api/stream-thoughts", stream=True
            )

            for line in response.iter_lines():
                if line:
                    # Decode the SSE event
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data: "):
                        event_data = decoded_line[6:]  # Remove 'data: ' prefix
                        display_status(event_data)  # Update UI with event data

            # If we reach here, the stream ended normally
            break

        except (requests.RequestException, ConnectionError) as e:
            retries += 1
            if retries > max_retries:
                print(f"Failed after {max_retries} retries: {e}")
                break

            # Exponential backoff
            delay = base_delay * (2 ** (retries - 1))
            print(f"Retry {retries} in {delay} seconds...")
            time.sleep(delay)


def display_status(data):
    """
    Function to process the incoming SSE data.
    """
    print(f"Status update: {data}")
    # Add your logic to handle different status messages
    # if "Failed" in data:
    #     handle_failure()
    # elif "Success" in data:
    #     handle_success()


# Example usage
if __name__ == "__main__":
    # The URL of your Flask blueprint's streaming endpoint
    STREAM_URL = "http://localhost:5000/api/stream-thoughts"
    stream_thoughts_client(STREAM_URL)

"""Option 3"""

import time

import requests

from backend.src.common.utils.retry_utils import \
    retry  # this "retry" might need to be adjusted based on actual imported

SSE_URL = "http://localhost:5000/stream-thoughts"


def display_status(msg):
    print(f"Status update: {msg}")


def sse_client():
    with requests.get(SSE_URL, stream=True) as response:
        if response.status_code != 200:
            raise Exception(f"Failed to connect: {response.status_code}")
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data: "):
                    display_status(decoded[6:])


@retry(max_attempts=2, backoff_factor=1.5, exceptions=(requests.ConnectionError,))
def run_sse_with_retry():
    sse_client()


if __name__ == "__main__":
    try:
        run_sse_with_retry()
    except Exception as e:
        print(f"Failed after retries: {e}")
