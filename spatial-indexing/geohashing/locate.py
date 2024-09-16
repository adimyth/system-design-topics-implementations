import math
from geohashing import geohash as geohash_encode
from reverse_geohashing import reverse_geohash as geohash_decode


def geohash_neighbor(geohash, dx, dy):
    """
    Return the neighbor of a geohash in a given direction.
    """
    # Decode the geohash of the center point to get the latitude and longitude
    latitude, longitude = geohash_decode(geohash)
    precision = len(geohash)
    # Each increment in the geohash precision level halves the width and height of the box
    # We reverse calculate the width and height of the box from the precision level

    # Longitude (width) uses 2.5 bits per character on average
    width = 360 / (2 ** (5 * precision // 2))
    # Latitude (height) uses 5 bits per character on average
    height = 180 / (2 ** (5 * precision // 2))
    # Calculate the latitude and longitude of the neighbor
    neighbor_lat = latitude + dy * height
    neighbor_lon = longitude + dx * width
    # Encode the latitude and longitude to get the geohash of the neighbor
    return geohash_encode((neighbor_lat, neighbor_lon), precision)


def geohash_neighbors(geohash):
    """
    Return the 8 neighbors of a geohash. There are 8 possible directions.

    Imagine a box around the geohash, with the geohash at the center. The box has 8 neighbors (assuming the precision 3 or more).
    """
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                # Skip the center geohash
                continue
            neighbors.append(geohash_neighbor(geohash, dx, dy))
    return neighbors


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on the Earth.

    The great circle distance is the shortest distance between two points along the surface of a sphere.
    """
    R = 6371  # Earth radius in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def get_precision(radius_km):
    """
    Return the geohash precision for a given radius in kilometers.

    Depending on the radius, we get a different geohash precision level.
    """
    if radius_km <= 0.019:
        return 9
    elif radius_km <= 0.076:
        return 8
    elif radius_km <= 0.61:
        return 7
    elif radius_km <= 2.4:
        return 6
    elif radius_km <= 19.5:
        return 5
    elif radius_km <= 78:
        return 4
    elif radius_km <= 630:
        return 3
    else:
        return 2


def geohash_radius_search(center, radius_km, points):
    """
    Return the points within a given radius of a center point.
    """

    # Get the geohash precision level based on the radius
    center_lat, center_lon = center
    precision = get_precision(radius_km)
    # Get the geohash of the center point
    center_hash = geohash_encode((center_lat, center_lon), precision)
    # Get the geohashes of the neighbors of the center point
    neighbor_hashes = geohash_neighbors(center_hash)
    # Include the center point in the search
    neighbor_hashes.append(center_hash)

    # For each point, check if it is within the radius of the center point
    for city, point in points.items():
        lat, lon = point
        point_hash = geohash_encode((lat, lon), precision)
        if point_hash in neighbor_hashes:
            distance = haversine_distance(center_lat, center_lon, lat, lon)
            if distance <= radius_km:
                print(f"{city}: {distance:.2f} km")


indian_cities = {
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.7041, 77.1025),
    "Bangalore": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Ahmedabad": (23.0225, 72.5714),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Surat": (21.1702, 72.8311),
    "Pune": (18.5204, 73.8567),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
}

# Search for points within a radius of X km from the center of Mumbai
center = (19.0760, 72.8777)  # Mumbai
radius_km = 1000

print(f"Points within {radius_km} km of {center}:")
geohash_radius_search(center, radius_km, indian_cities)
