import hashlib
import bisect
from typing import List


class Node:
    def __init__(self, node_id: int, node_name: str, node_ip: str) -> None:
        """
        Initializes the class

        :param node_id: The id of the node
        :param node_name: The name of the node
        """
        self.node_id = node_id
        self.node_name = node_name
        self.node_ip = node_ip

    def __repr__(self) -> str:
        return f"Node({self.node_id}, {self.node_name}, {self.node_ip})"


class ConsistentHashing:
    def __init__(self, nodes: List[Node] = None, num_replicas: int = 100) -> None:
        """
        Initializes the class

        :param nodes: List of nodes. This is the initial set of nodes in the system.

        :num_replicas: The number of replicas of each node to place on the ring.
        """

        self.num_replicas = num_replicas
        # Ring maps hash value to nodes. It contains the hash values of both real nodes and virtual nodes.
        self.ring = {}
        # Stores the hash values of nodes in sorted order. Used to efficiently find the node for a key using binary search.
        self.sorted_hashes = []

        for node in nodes:
            self.add_node(node)

    def hash(self, key: str) -> int:
        """
        Takes in a key (node, node replica, data point) and returns the hash value in the range [0, 2^128 - 1]
        """
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: Node) -> None:
        """
        Adds a node to the ring along with its replicas.
        """
        for i in range(self.num_replicas):
            node_hash = self.hash(f"{node.node_id}_{i}")
            self.ring[node_hash] = node
            # Maintain a sorted list of hashes for efficient lookup later.
            bisect.insort(self.sorted_hashes, node_hash)

    def remove_node(self, node: Node) -> None:
        """
        Removes a node from the ring along with its replicas.
        """
        for i in range(self.num_replicas):
            node_hash = self.hash(f"{node.node_id}_{i}")
            del self.ring[node_hash]
            self.sorted_hashes.remove(node_hash)

    def get_node(self, key: str) -> Node:
        """
        Returns the node responsible for a given key
        """

        key_hash = self.hash(key)
        # Find the index of the first node hash that is greater than or equal to the key hash.
        idx = bisect.bisect(self.sorted_hashes, key_hash)

        # If the key hash is greater than all node hashes, then the index will be 0 (wrap around).
        if idx == len(self.sorted_hashes):
            idx = 0
        return self.ring[self.sorted_hashes[idx]]


if __name__ == "__main__":
    # Create 3 nodes
    node1 = Node(1, "node1", "192.168.1.1")
    node2 = Node(2, "node2", "192.169.1.1")
    node3 = Node(3, "node3", "192.170.1.1")

    # Create a consistent hashing ring with the 3 nodes
    ch = ConsistentHashing([node1, node2, node3])

    # Create 10 data points
    data_points = [f"data{i}" for i in range(10)]

    # Print the node responsible for each data point
    print(f"Initial mapping of data points to nodes")
    initial_mapping = {}
    for data_point in data_points:
        initial_mapping[data_point] = ch.get_node(data_point)
        print(f"{data_point}: {ch.get_node(data_point)}")

    # Add 2 new nodes
    node4 = Node(4, "node4", "192.171.1.1")
    ch.add_node(node4)
    node5 = Node(5, "node5", "192.172.1.1")
    ch.add_node(node5)

    # Check the node responsible for each data point again
    print(f"\nMapping of data points to nodes after adding 2 new nodes")
    remapping = {}
    for data_point in data_points:
        remapping[data_point] = ch.get_node(data_point)
        print(f"{data_point}: {ch.get_node(data_point)}")

    # Number of data points that are remapped to a different node after adding 2 new nodes
    num_remapped = 0
    for data_point in data_points:
        if initial_mapping[data_point] != remapping[data_point]:
            num_remapped += 1
    print(f"\nNumber of data points remapped to a different node: {num_remapped}")
