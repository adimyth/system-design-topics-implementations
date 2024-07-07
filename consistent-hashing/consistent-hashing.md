# Consistent Hashing

The issue with simple hashing is that when a server is added or removed, the majority of the keys need to be remapped. Consistent hashing is a technique that minimizes the number of keys that need to be remapped when a server is added or removed.

1. This is used in distributed systems to distribute data across multiple servers. It is used in systems like load balancers, distributed caches, and distributed databases.
2. Amazon Dynamo, Cassandra, and Memcached use consistent hashing for data partitioning.
3. CDN (Content Delivery Network) uses consistent hashing to distribute content evenly across edge servers.
4. 

> This is especially useful in distributed systems where the number of servers can change dynamically.


## Hash Space
A hash function maps keys to integers. The hash space is the range of values that the hash function can output. For example, if the hash function outputs a 32-bit integer, the hash space is 2^32.

*Here we are using MD5 hash function which outputs a 128-bit integer. The hash space is 2^128.*

```python
def hash(self, key: str) -> int:
    """
    Takes in a key (node &node replica or data point) and returns the hash value in the range [0, 2^128 - 1]
    """
    return int(hashlib.md5(key.encode()).hexdigest(), 16)
```

## Hash Ring
1. The hash ring is a circle with the hash space. Each server is mapped to a point on the hash ring. The hash ring wraps around, so the first point is adjacent to the last point.
2. We can use the IP address or the name of the server to map the server to a point on the hash ring.

*Here we are using the MD5 hash of `{node.id}_{replica_number}` to map the server to a point on the hash ring.*

```python
def add_node(self, node: Node) -> None:
    """
    Adds a node to the ring along with its replicas.
    """
    for i in range(self.num_replicas):
        node_hash = self.hash(f"{node.node_id}_{i}")
        self.ring[node_hash] = node
```

## Mapping Data Points
Similarly, we can use the MD5 hash of the data point to map the data point to a point on the hash ring.

To assign a data point to the server, we go clockwise & find the next server on the hash ring. The server that is responsible for the data point is the first server that we encounter.

> ![NOTE]
> *In our case, we  are using `bisect.bisect` to find the index of the first node hash that is greater than or equal to the key hash.*

```python
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

mapping = {}
for data_point in data_points:
    mapping[data_point] = ch.get_node(data_point)
    print(f"{data_point}: {ch.get_node(data_point)}")
```

## Adding a new server
Let's assume that originally, the hash ring initially had 3 servers and 9 data points & it looked like this:

![Original mapping](https://i.imgur.com/gEV1UOI.png)

1️⃣ When a new server is added, we add the server to the hash ring along with it's replicas.

*Here, we add the server to the hash ring along with its replicas. We maintain a sorted list of hashes for efficient lookup later.*

```python
def add_node(self, node: Node) -> None:
    """
    Adds a node to the ring along with its replicas.
    """
    for i in range(self.num_replicas):
        node_hash = self.hash(f"{node.node_id}_{i}")
        self.ring[node_hash] = node
        # Maintain a sorted list of hashes for efficient lookup later.
        bisect.insort(self.sorted_hashes, node_hash)
```

2️⃣ We then need to remap the affected data points to the new server. Here, not all the data points need to be remapped.

```python
    node4 = Node(4, "node4", "192.171.1.1")
    ch.add_node(node4)

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
```

![Remapping after adding a new server](https://i.imgur.com/AHoADO9.png)

**Here, after adding a new server `S4`, which lies between `S2` & `S3`, only 2 data points (`DP4` & `DP5`) that were earlier mapped to `S3` are remapped to `S4`. The rest of the data points remain mapped to their original servers.**

## Removing a server
1️⃣ When a server is removed, we remove the server from the hash ring.

```python
def remove_node(self, node: Node) -> None:
    """
    Removes a node from the ring along with its replicas.
    """
    for i in range(self.num_replicas):
        node_hash = self.hash(f"{node.node_id}_{i}")
        del self.ring[node_hash]
        self.sorted_hashes.remove(node_hash)
```

2️⃣ We then need to remap the affected data points to the next server.

```python
    ch.remove_node(node2)

    # Check the node responsible for each data point again
    print(f"\nMapping of data points to nodes after removing node2")
    remapping = {}
    for data_point in data_points:
        remapping[data_point] = ch.get_node(data_point)
        print(f"{data_point}: {ch.get_node(data_point)}")

    # Number of data points that are remapped to a different node after removing node2
    num_remapped = 0
    for data_point in data_points:
        if initial_mapping[data_point] != remapping[data_point]:
            num_remapped += 1
    print(f"\nNumber of data points remapped to a different node: {num_remapped}")
```


## Limitations
### Load Imbalance
The distribution of data points across servers may not be uniform. Some servers may have more data points than others. This is because -
   1. the hash function may not distribute the servers uniformly across the hash space, hence the area of the hash ring that a server is responsible for may not be uniform.
   2. the data points may not be uniformly distributed across the hash space.

*The solution is to use replicas. Each server is mapped to multiple points on the hash ring. This ensures that the data points are distributed more uniformly across the servers. As the number of virtual nodes (replicas) increases, the distribution of the load becomes more balanced*