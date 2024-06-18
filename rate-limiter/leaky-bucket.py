import random
import threading
import time
from typing import Tuple


class Packet:
    def __init__(self, size: int):
        self.size = size  # packet size in bytes


class LeakyBucket:
    def __init__(self, bucket_size: int, rate: Tuple[int, int]):
        self.bucket_size = bucket_size  # bucket size
        self.rate = rate  # leaky rate. eg - (500, 2) implies 500 bytes every 2 seconds
        self.current_size = 0  # current filled bucket size
        self.lock = threading.Lock()  # for synchronizing access to the bucket
        self.stop_event = (
            threading.Event()
        )  # for synchronizing the start/stop event in transmission

    def add_packet(self, packet: Packet):
        with self.lock:
            if (self.current_size + packet.size) > self.bucket_size:
                print(f"Capacity Full. Dropping the Packet")
                return

            self.current_size += packet.size
            print(f"New packet: {packet.size}. Current size: {self.current_size}")

    def transmit(self):
        while not self.stop_event.is_set():
            with self.lock:
                if self.current_size <= 0:
                    print(f"Nothing to transmit. Bucket Empty")
                else:
                    self.current_size -= min(self.rate[0], self.current_size)
                    print(f"Transmitted Packets. Current Size: {self.current_size}")
            # transmit packets after a certain duration
            time.sleep(self.rate[1])

    def start_transmission(self):
        self.transmission_thread = threading.Thread(target=self.transmit)
        self.transmission_thread.start()

    def stop_transmission(self):
        self.stop_event.set()
        self.transmission_thread.join()


if __name__ == "__main__":
    leaky_bucket = LeakyBucket(bucket_size=1000, rate=(500, 2))

    # start the transmission
    leaky_bucket.start_transmission()

    # simulating a bursty traffic by inserting N number of packets of different sizes (from 0 to 600 bytes)
    packet_size = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600]
    n = 20
    for i in range(n):
        leaky_bucket.add_packet(Packet(size=random.choice(packet_size)))
        # adding a random delay between packets arrival
        time.sleep(random.uniform(0.1, 1.0))

    # stop the transmission & the program after 30 seconds
    time.sleep(30)
    leaky_bucket.stop_transmission()
