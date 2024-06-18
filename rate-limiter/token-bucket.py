import random
import threading
import time
from typing import Tuple


class TokenBucket:
    def __init__(self, bucket_size: int, refresh_rate: Tuple[int, int]) -> None:
        self.bucket_size = bucket_size
        self.refresh_rate = refresh_rate  # (tokens, seconds)
        self.tokens = 0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def add_token(self) -> None:
        while not self.stop_event.is_set():
            # Add token to the bucket if it is not full based on the refresh rate
            with self.lock:
                if self.tokens < self.bucket_size:
                    self.tokens += self.refresh_rate[0]
                    if self.tokens > self.bucket_size:
                        self.tokens = self.bucket_size
                    print(f"Added token. Current tokens: {self.tokens}")
                else:
                    print(f"Bucket Full. Discarding token")
            time.sleep(self.refresh_rate[1])

    def consume_token(self) -> None:
        with self.lock:
            if self.tokens <= 0:
                print(f"No tokens available for consumption. Bucket Empty")
            else:
                self.tokens -= 1
                print(f"Transmitted packet. Current tokens: {self.tokens}")

    def start(self):
        self.add_token_thread = threading.Thread(target=self.add_token)
        self.add_token_thread.start()

    def stop(self):
        self.stop_event.set()
        self.add_token_thread.join()


if __name__ == "__main__":
    token_bucket = TokenBucket(bucket_size=5, refresh_rate=(1, 1))

    # Start the transmission
    token_bucket.start()

    # Simulating a bursty traffic by sending N number of requests
    n = 5
    for i in range(n):
        token_bucket.consume_token()
        # Simulate random time between requests
        time.sleep(random.randint(1, 3))

    # Stop the transmission after a certain duration
    time.sleep(2)
    token_bucket.stop()
