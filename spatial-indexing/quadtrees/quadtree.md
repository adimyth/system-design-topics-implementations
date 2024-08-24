## Memory Requirements

**Data stored in an internal node**
| Field            | Description                                                  | Size (bytes) |
| ---------------- | ------------------------------------------------------------ | ------------ |
| topLeft          | Coordinates (x, y) of the top left corner of the node        | 16 (8 * 2)   |
| bottomRight      | Coordinates (x, y) of the bottom right corner of the node    | 16 (8 * 2)   |
| topLeftChild     | Pointer to the top left child node                           | 8            |
| topRightChild    | Pointer to the top right child node                          | 8            |
| bottomLeftChild  | Pointer to the bottom left child node                        | 8            |
| bottomRightChild | Pointer to the bottom right child node                       | 8            |
| isLeaf           | Flag to indicate if the node is a leaf node                  | 1            |
| capacity         | Maximum number of data points that can be stored in the node | 4            |

> Total is 69 bytes.

**Data stored in a leaf node**
We are storing a city as a data point in the leaf node. A city has the following fields:
* Location (latitude, longitude) - 2 * 8 = 16 bytes
* Name - 16 bytes
It takes 32 bytes to store a city.


| Field       | Description                                                  | Size (bytes) |
| ----------- | ------------------------------------------------------------ | ------------ |
| topLeft     | Coordinates (x, y) of the top left corner of the node        | 16 (8 * 2)   |
| bottomRight | Coordinates (x, y) of the bottom right corner of the node    | 16 (8 * 2)   |
| cities      | List of cities stored in the leaf node (max 4)               | 4*32         |
| isLeaf      | Flag to indicate if the node is a leaf node                  | 1            |
| capacity    | Maximum number of data points that can be stored in the node | 4            |

> Total is 145 bytes.

**Total memory required**
If we are storing 1 million cities, we would need:

* Each grid can store a maximum of 4 cities.
* Number of leaf nodes ~ 1 million / 4 = 250,000
* Number of internal nodes ~ (Number of leaf nodes)/3 = 83,333
* Total memory required ~ (250,000 * 145) + (83,333 * 69) = 36.25 MB + 5.75 MB = 42 MB

[Relation between internal and leaf nodes in a quadtree](https://stackoverflow.com/questions/35976444/how-many-leaves-has-a-quadtree)

## Time Complexity

### Creating the quadtree for N points
The time complexity of creating a quadtree for N points is `O(N log N)`. We have N points and for each point, we need to traverse the tree from the root to the leaf node. The height of the tree is log N.

### Inserting a point
The time complexity of inserting a point is `O(log N)`. We need to traverse the tree from the root to the leaf node.

### Radius search

**Worst case**
If there's only one leaf node in the search radius, the time complexity would be `O(N)`.

**Average case**
The average time complexity of a radius search `O(log N + k)`, where k is the number of points in the search radius.

This is because we take `O(log N)` time to reach the leaf node and `O(k)` time to collect the points in the search radius.