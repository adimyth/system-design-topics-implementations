from abc import ABC
import random
from typing import List
import matplotlib.pyplot as plt


class Point(ABC):
    """
    A point in 2D space.
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Node(ABC):
    """
    A node in the point quadtree.

    Attributes
    ----------
    x: float
        The x-coordinate of the center of the bounding box.
    y: float
        The y-coordinate of the center of the bounding box.
    w : float
        The width of the bounding box.
    h : float
        The height of the bounding box.
    TL : Node
        The top-left child node.
    TR : Node
        The top-right child node.
    BL : Node
        The bottom-left child node.
    BR : Node
        The bottom-right child node.
    points : List[Point]
        A list of points that fall within the bounding box & belong to the node.
    """

    def __init__(self, x: float, y: float, w: float, h: float, points: List[Point]):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.TL: Node = None
        self.TR: Node = None
        self.BL: Node = None
        self.BR: Node = None
        self.points = points


def recursive_subdivide(node: Node, threshold: int):
    """
    Recursively subdivide the node into 4 quadrants.
    """
    # Divide the node into 4 quadrants only if the number of points in the node exceeds the threshold.
    if len(node.points) > threshold:
        w = node.w / 2
        h = node.h / 2
        node.TL = Node(x=node.x - w / 2, y=node.y + h / 2, w=w, h=h, points=[])
        node.TR = Node(x=node.x + w / 2, y=node.y + h / 2, w=w, h=h, points=[])
        node.BL = Node(x=node.x - w / 2, y=node.y - h / 2, w=w, h=h, points=[])
        node.BR = Node(x=node.x + w / 2, y=node.y - h / 2, w=w, h=h, points=[])
        for point in node.points:
            if point.x < node.x:
                if point.y < node.y:
                    node.BL.points.append(point)
                else:
                    node.TL.points.append(point)
            else:
                if point.y < node.y:
                    node.BR.points.append(point)
                else:
                    node.TR.points.append(point)
        for child in [node.TL, node.TR, node.BL, node.BR]:
            recursive_subdivide(child, threshold)


class QuadTree:
    """
    A quadtree containing a collection of nodes.

    Attributes
    ----------
    threshold : int
        The maximum number of points in a node before it splits.
    h: int
        The initial size of the quadtree root node bounding box.
    w: int
        The initial size of the quadtree root node bounding box.
    """

    def __init__(self, threshold: int, w: int, h: int):
        self.threshold = threshold
        # randomly generate the initial points
        self.points = [
            Point(random.uniform(0, w), random.uniform(0, h)) for _ in range(100)
        ]
        self.root = Node(x=w / 2, y=h / 2, w=w, h=h, points=self.points)

    def subdivide(self):
        """
        Subdivide the root node into 4 quadrants.
        """
        recursive_subdivide(self.root, self.threshold)

    def query(self, x: float, y: float):
        """
        Query the quadtree for points within a bounding box.
        """

        def recursive_query(node: Node, x: float, y: float):
            if not node:
                return []
            if x - node.w / 2 > node.x and y + node.h / 2 < node.y:
                return recursive_query(node.TR, x, y)
            elif x + node.w / 2 < node.x and y + node.h / 2 < node.y:
                return recursive_query(node.TL, x, y)
            elif x - node.w / 2 > node.x and y - node.h / 2 > node.y:
                return recursive_query(node.BR, x, y)
            elif x + node.w / 2 < node.x and y - node.h / 2 > node.y:
                return recursive_query(node.BL, x, y)
            return node.points

        return recursive_query(self.root, x, y)

    def insert(self, x: float, y: float):
        """
        Insert a point into the quadtree.
        """

        def recursive_insert(node: Node, x: float, y: float):
            if (
                x < node.x - node.w / 2
                or x > node.x + node.w / 2
                or y < node.y - node.h / 2
                or y > node.y + node.h / 2
            ):
                return
            if len(node.points) < self.threshold:
                node.points.append(Point(x, y))
            else:
                if not node.TL:
                    recursive_subdivide(node, self.threshold)
                if x < node.x:
                    if y < node.y:
                        recursive_insert(node.BL, x, y)
                    else:
                        recursive_insert(node.TL, x, y)
                else:
                    if y < node.y:
                        recursive_insert(node.BR, x, y)
                    else:
                        recursive_insert(node.TR, x, y)

        recursive_insert(self.root, x, y)

    def plot(self):
        """
        Plot the quadtree.
        """

        def recursive_plot(node: Node):
            if not node:
                return
            plt.plot(
                [node.x - node.w / 2, node.x + node.w / 2],
                [node.y + node.h / 2, node.y + node.h / 2],
                color="black",
            )
            plt.plot(
                [node.x - node.w / 2, node.x + node.w / 2],
                [node.y - node.h / 2, node.y - node.h / 2],
                color="black",
            )
            plt.plot(
                [node.x - node.w / 2, node.x - node.w / 2],
                [node.y - node.h / 2, node.y + node.h / 2],
                color="black",
            )
            plt.plot(
                [node.x + node.w / 2, node.x + node.w / 2],
                [node.y - node.h / 2, node.y + node.h / 2],
                color="black",
            )
            for point in node.points:
                plt.scatter(point.x, point.y, color="black")
            for child in [node.TL, node.TR, node.BL, node.BR]:
                recursive_plot(child)

        recursive_plot(self.root)
        plt.show()


if __name__ == "__main__":
    quadtree = QuadTree(threshold=5, w=100, h=100)
    quadtree.subdivide()
    quadtree.plot()
    quadtree.insert(10, 10)
    quadtree.insert(90, 90)
    quadtree.insert(95, 95)
    quadtree.insert(93, 93)
    quadtree.plot()
