from dataclasses import dataclass, field
from typing import List
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches


@dataclass
class Coordinate:
    """
    A simple data class to represent a 2D coordinate.

    Attributes:
    x: float - The x-coordinate.
    y: float - The y-coordinate.
    """

    x: float
    y: float


@dataclass
class Cities:
    """
    A simple data class to represent a city.

    Attributes:
    name: str - The name of the city.
    location: Coordinate - The location of the city.
    """

    name: str
    location: Coordinate


@dataclass
class Quadtree:
    """
    A Quadtree represents a region in a 2D space. It is a tree data structure in which each internal node has exactly four children.

    The internal nodes of the Quadtree are represented by the Quadtree class itself. The leaf nodes store the data (cities in this case).

    Attributes:
    capacity: int - The maximum number of cities that can be stored in a leaf node. If the number of cities exceeds this capacity, the leaf node is split into four child nodes. The default value is 4.
    topLeft: Coordinate - The top-left corner of the region represented by the Quadtree.
    bottomRight: Coordinate - The bottom-right corner of the region represented by the Quadtree.
    topLeftChild: Quadtree - The Quadtree representing the top-left quadrant of the region.
    topRightChild: Quadtree - The Quadtree representing the top-right quadrant of the region.
    bottomLeftChild: Quadtree - The Quadtree representing the bottom-left quadrant of the region.
    bottomRightChild: Quadtree - The Quadtree representing the bottom-right quadrant of the region.
    cities: List[Cities] - The list of cities stored in the Quadtree (only present in leaf nodes).
    isLeaf: bool - A flag to indicate whether the Quadtree is a leaf node or an internal node. The default value is True.
    """

    capacity: int = 4
    topLeft: Coordinate = None
    bottomRight: Coordinate = None
    topLeftChild: "Quadtree" = None
    topRightChild: "Quadtree" = None
    bottomLeftChild: "Quadtree" = None
    bottomRightChild: "Quadtree" = None
    cities: list[Cities] = field(default_factory=list)
    isLeaf: bool = True

    def withinBoundaries(self, quadtree: "Quadtree", city: Cities) -> bool:
        """
        Checks if a city is within the boundaries of the Quadtree.

        Parameters:
        quadtree (Quadtree): The Quadtree representing the region.
        city (Cities): The city to be checked.
        """
        # Check if the x-coordinate of the city is within the x-coordinates of the Quadtree. Do the same for the y-coordinate.
        return (quadtree.topLeft.x <= city.location.x <= quadtree.bottomRight.x) and (
            quadtree.topLeft.y >= city.location.y >= quadtree.bottomRight.y
        )

    def insert(self, quadtree: "Quadtree", city: Cities) -> "Quadtree":
        """
        Inserts a city into the Quadtree.

        Parameters:
        quadtree (Quadtree): The Quadtree representing the region.
        city (Cities): The city to be inserted.

        Returns:
        Quadtree: The Quadtree after inserting the city.

        Algorithm:
        1. If the city is not within the boundaries of the Quadtree, return the Quadtree as is.
        2. If the Quadtree is a leaf node and has space, insert the city.
        3. If the Quadtree is a leaf node and is full, split it i.e create four child nodes and redistribute the existing cities among them.
        4. If we reach here, the node is not a leaf (either it was split just now or it was already an internal node). So we need to insert the city into the appropriate child.
        5. Return the Quadtree after inserting the city.
        """
        # If the city is not within the boundaries of the Quadtree, return the Quadtree as is.
        if not self.withinBoundaries(quadtree, city):
            return quadtree

        # If the Quadtree is a leaf node and has space, insert the city
        if quadtree.isLeaf and len(quadtree.cities) < quadtree.capacity:
            quadtree.cities.append(city)
            return quadtree

        # If the Quadtree is a leaf node and is full, split it
        if quadtree.isLeaf and len(quadtree.cities) == quadtree.capacity:
            self._split_node(quadtree)
            # Note: At this point, quadtree is no longer a leaf

        # If we reach here, the node is not a leaf (either it was split just now or it was already an internal node)
        # So we need to insert the city into the appropriate child
        self._insert_into_child(quadtree, city)

        return quadtree

    def _split_node(self, quadtree: "Quadtree"):
        midX = (quadtree.topLeft.x + quadtree.bottomRight.x) / 2
        midY = (quadtree.topLeft.y + quadtree.bottomRight.y) / 2

        quadtree.topLeftChild = Quadtree(
            topLeft=quadtree.topLeft,
            bottomRight=Coordinate(midX, midY),
            capacity=quadtree.capacity,
        )
        quadtree.topRightChild = Quadtree(
            topLeft=Coordinate(midX, quadtree.topLeft.y),
            bottomRight=Coordinate(quadtree.bottomRight.x, midY),
            capacity=quadtree.capacity,
        )
        quadtree.bottomLeftChild = Quadtree(
            topLeft=Coordinate(quadtree.topLeft.x, midY),
            bottomRight=Coordinate(midX, quadtree.bottomRight.y),
            capacity=quadtree.capacity,
        )
        quadtree.bottomRightChild = Quadtree(
            topLeft=Coordinate(midX, midY),
            bottomRight=quadtree.bottomRight,
            capacity=quadtree.capacity,
        )

        # Redistribute existing cities
        for existing_city in quadtree.cities:
            # Find the child node in which the city should be inserted (here the recursion depth will be most likely 1)
            self._insert_into_child(quadtree, existing_city)

        quadtree.cities = None
        quadtree.isLeaf = False

    def _insert_into_child(self, quadtree: "Quadtree", city: Cities):
        midX = (quadtree.topLeft.x + quadtree.bottomRight.x) / 2
        midY = (quadtree.topLeft.y + quadtree.bottomRight.y) / 2

        if city.location.x < midX:
            if city.location.y > midY:
                self.insert(quadtree.topLeftChild, city)
            else:
                self.insert(quadtree.bottomLeftChild, city)
        else:
            if city.location.y > midY:
                self.insert(quadtree.topRightChild, city)
            else:
                self.insert(quadtree.bottomRightChild, city)

    def visualize(self, quadtree: "Quadtree", ax=None, level=0):
        """
        Steps:

        1. Create a rectangle patch using the top-left and bottom-right coordinates of the Quadtree.
            a. Create a figure of size 10x10.
            b. Set the x and y limits of the plot as the x and y coordinates of the Quadtree.
        2. Plot the rectangle using the top-left and bottom-right coordinates.
            a. If the Quadtree is an internal node, fill the rectangle with orange color. Also, add the level annotation.
            b. If the Quadtree is a leaf node, fill the rectangle with green color.
        3. If the Quadtree is a leaf node and has cities, plot the cities.
            a. Plot the city locations as red dots.
            b. Add the city names as text.
        4. If the Quadtree is not a leaf node, recursively call the visualize function on its children.
        """
        if ax is None:
            _, ax = plt.subplots(figsize=(10, 10))
            ax.set_xlim(quadtree.topLeft.x, quadtree.bottomRight.x)
            ax.set_ylim(quadtree.bottomRight.y, quadtree.topLeft.y)
            ax.set_aspect("equal")
            ax.set_title("Quadtree Visualization")

        width = quadtree.bottomRight.x - quadtree.topLeft.x
        height = quadtree.topLeft.y - quadtree.bottomRight.y

        # Plot rectangle for internal node
        if not quadtree.isLeaf:
            rect = patches.Rectangle(
                (quadtree.topLeft.x, quadtree.bottomRight.y),
                width,
                height,
                fill=False,
                color="orange",
                linewidth=5,
            )
            ax.add_patch(rect)
            # Add level annotation
            rx, ry = rect.get_xy()
            cx = rx + rect.get_width() / 2.0
            cy = ry + rect.get_height() / 2.0
            ax.annotate(
                f"Level: {level}",
                (cx, cy),
                color="black",
                weight="bold",
                fontsize=10,
                ha="center",
                va="center",
            )

        # Plot rectangle for leaf node
        if quadtree.isLeaf:
            rect = patches.Rectangle(
                (quadtree.topLeft.x, quadtree.bottomRight.y),
                width,
                height,
                fill=False,
                color="green",
                linewidth=1,
            )
            ax.add_patch(rect)

            # Plot red markers for cities
            if len(quadtree.cities) > 0:
                for city in quadtree.cities:
                    ax.plot(city.location.x, city.location.y, "ro", markersize=4)
                    ax.text(
                        city.location.x,
                        city.location.y,
                        city.name,
                        fontsize=10,
                        ha="right",
                        va="bottom",
                    )

        if not quadtree.isLeaf:
            self.visualize(quadtree.topLeftChild, ax, level=level + 1)
            self.visualize(quadtree.topRightChild, ax, level=level + 1)
            self.visualize(quadtree.bottomLeftChild, ax, level=level + 1)
            self.visualize(quadtree.bottomRightChild, ax, level=level + 1)

        if level == 0:
            plt.show()

    @staticmethod
    def check_overlap(
        point: Coordinate, radius: int, topLeft: Coordinate, bottomRight: Coordinate
    ) -> bool:
        """
        Checks if a circle with a given radius centered at a point overlaps with a rectangle.

        Parameters:
        point (Coordinate): The center of the circle.
        radius (int): The radius of the circle.
        topLeft (Coordinate): The top-left corner of the rectangle.
        bottomRight (Coordinate): The bottom-right corner of the rectangle.

        Returns:
        bool: True if the circle overlaps with the rectangle, False otherwise.

        Algorithm:
        1. If the point lies inside the rectangle, return True.
        2. Find the closest point on the rectangle to the circle.
        3. Calculate the distance between the point and the closest point.
        4. Convert the distance to kilometers. (this is an approximation)
        5. Check if the distance is less than or equal to the radius.
        """
        if is_point_inside_rect(point, topLeft, bottomRight):
            return True

        closest_lon = max(topLeft.x, min(point.x, bottomRight.x))
        closest_lat = max(bottomRight.y, min(point.y, topLeft.y))

        lat_diff = abs(point.y - closest_lat)
        lon_diff = abs(point.x - closest_lon)

        lat_km, lon_km = degrees_to_kilometers(lat_diff, lon_diff, point.y)
        distance_km = math.sqrt(lat_km**2 + lon_km**2)

        return distance_km <= radius

    def radiusSearch(self, point: Coordinate, radius: int):
        result = []

        if not self.check_overlap(point, radius, self.topLeft, self.bottomRight):
            return result

        if self.isLeaf:
            for city in self.cities:
                lat_diff = abs(city.location.y - point.y)
                lon_diff = abs(city.location.x - point.x)
                lat_km, lon_km = degrees_to_kilometers(lat_diff, lon_diff, point.y)
                distance_km = math.sqrt(lat_km**2 + lon_km**2)

                if distance_km <= radius:
                    result.append((city, distance_km))
        else:
            for child in [
                self.topLeftChild,
                self.topRightChild,
                self.bottomLeftChild,
                self.bottomRightChild,
            ]:
                if child:
                    result.extend(child.radiusSearch(point, radius))

        return result


def to_radians(deg: int) -> float:
    """
    Converts degrees to radians.
    """
    return deg * math.pi / 180.0


def degrees_to_kilometers(
    lat_diff: float, lon_diff: float, latitude: float
) -> tuple[float, float]:
    """
    Converts the difference in latitude and longitude to kilometers.
    """
    lat_km = lat_diff * 111.0
    lon_km = lon_diff * 111.0 * math.cos(to_radians(latitude))
    return lat_km, lon_km


def is_point_inside_rect(
    point: Coordinate, topLeft: Coordinate, bottomRight: Coordinate
):
    """
    Checks if a point lies within the boundaries of a rectangle.
    """
    return (topLeft.x <= point.x <= bottomRight.x) and (
        bottomRight.y <= point.y <= topLeft.y
    )


if __name__ == "__main__":
    # Create a Quadtree representing India
    india = Quadtree(
        topLeft=Coordinate(68.1766451354, 37.09024),
        bottomRight=Coordinate(97.4025614766, 8.088306427),
    )

    # Insert some locations in India into the Quadtree
    # Mumbai (19.0760° N, 72.8777° E)
    mumbai = Cities(name="Mumbai", location=Coordinate(72.8777, 19.0760))
    india.insert(india, mumbai)

    # Delhi (28.7041° N, 77.1025° E)
    delhi = Cities(name="Delhi", location=Coordinate(77.1025, 28.7041))
    india.insert(india, delhi)

    # Pune (18.5204° N, 73.8567° E)
    pune = Cities(name="Pune", location=Coordinate(73.8567, 18.5204))
    india.insert(india, pune)

    # Bangalore (12.9716° N, 77.5946° E)
    bangalore = Cities(name="Bangalore", location=Coordinate(77.5946, 12.9716))
    india.insert(india, bangalore)

    # Kolkata (22.5726° N, 88.3639° E)
    kolkata = Cities(name="Kolkata", location=Coordinate(88.3639, 22.5726))
    india.insert(india, kolkata)

    # Chennai (13.0827° N, 80.2707° E)
    chennai = Cities(name="Chennai", location=Coordinate(80.2707, 13.0827))
    india.insert(india, chennai)

    # Surat (21.1702° N, 72.8311° E)
    surat = Cities(name="Surat", location=Coordinate(72.8311, 21.1702))
    india.insert(india, surat)

    # Jaipur (26.9124° N, 75.7873° E)
    jaipur = Cities(name="Jaipur", location=Coordinate(75.7873, 26.9124))
    india.insert(india, jaipur)

    # Ahmedabad (23.0225° N, 72.5714° E)
    ahmedabad = Cities(name="Ahmedabad", location=Coordinate(72.5714, 23.0225))
    india.insert(india, ahmedabad)

    # Hyderabad (17.3850° N, 78.4867° E)
    hyderabad = Cities(name="Hyderabad", location=Coordinate(78.4867, 17.3850))
    india.insert(india, hyderabad)

    # Indore (22.7196° N, 75.8577° E)
    indore = Cities(name="Indore", location=Coordinate(75.8577, 22.7196))
    india.insert(india, indore)

    # Lucknow (26.8467° N, 80.9462° E)
    lucknow = Cities(name="Lucknow", location=Coordinate(80.9462, 26.8467))
    india.insert(india, lucknow)

    # Kanpur (26.4499° N, 80.3319° E)
    kanpur = Cities(name="Kanpur", location=Coordinate(80.3319, 26.4499))
    india.insert(india, kanpur)

    # Nagpur (21.1458° N, 79.0882° E)
    nagpur = Cities(name="Nagpur", location=Coordinate(79.0882, 21.1458))
    india.insert(india, nagpur)

    # Visakhapatnam (17.6868° N, 83.2185° E)
    visakhapatnam = Cities(name="Visakhapatnam", location=Coordinate(83.2185, 17.6868))
    india.insert(india, visakhapatnam)

    # Bhopal (23.2599° N, 77.4126° E)
    bhopal = Cities(name="Bhopal", location=Coordinate(77.4126, 23.2599))
    india.insert(india, bhopal)

    # Patna (25.5941° N, 85.1376° E)
    patna = Cities(name="Patna", location=Coordinate(85.1376, 25.5941))
    india.insert(india, patna)

    # Ludhiana (30.9010° N, 75.8573° E)
    ludhiana = Cities(name="Ludhiana", location=Coordinate(75.8573, 30.9010))
    india.insert(india, ludhiana)

    # Visualize the Quadtree
    india.visualize(india)

    # Perform a radius search around Mumbai with a radius of 1000 km
    mumbai_location = Coordinate(72.8777, 19.0760)
    radius = 700
    cities = india.radiusSearch(mumbai_location, radius)

    print(f"Cities within {radius} km of Mumbai:")
    # Sort the cities based on distance
    cities.sort(key=lambda x: x[1])
    for city, distance in cities:
        print(f"{city.name} - Distance: {distance:.2f} km")
