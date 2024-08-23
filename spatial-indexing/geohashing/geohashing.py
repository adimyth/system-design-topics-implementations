def get_longitude_representation(longitude: float, precision: float) -> str:
    """
    Longitude is along the x-axis.

    Interval Range: [-180, 180).

    Operation:
    1. We partition the interval into 2 equal parts. If the longitude lies to the left of the midpoint assign it 0, otherwise assign 1.
    2. The midpoint belongs to the right interval. Ex - when dividing the interval [-180, 180) into 2 parts, the midpoint belongs to the right interval.
    3. We continue this process until we reach the desired precision.
    """
    left_boundary, right_boundary = -180, 180
    representation = ""
    for i in range(precision):
        midpoint = (left_boundary + right_boundary) / 2
        if longitude < midpoint:
            representation += "0"
            right_boundary = midpoint
        else:
            representation += "1"
            left_boundary = midpoint
    return representation


def get_latitude_representation(latitude: float, precision: float) -> str:
    """
    Latitude is along the y-axis.

    Interval Range: [-90, 90).

    Operation:
    1. We partition the interval into 2 equal parts. If the latitude lies above the midpoint assign it 0, otherwise assign 1.
    2. The midpoint belongs to the lower interval. Ex - when dividing the interval [-90, 90) into 2 parts, the midpoint belongs to the lower interval.
    3. We continue this process until we reach the desired precision.
    """
    top_boundary, bottom_boundary = 90, -90
    representation = ""
    for i in range(precision):
        midpoint = (top_boundary + bottom_boundary) / 2
        if latitude < midpoint:
            representation += "0"
            top_boundary = midpoint
        else:
            representation += "1"
            bottom_boundary = midpoint
    return representation


def interleave_bits(longitude_representation: str, latitude_representation: str) -> str:
    """
    Interleave the bits of x and y.

    Example
    -------
    x = 1010
    y = 1100

    Interleaved bits = 11100010
    """
    return "".join(
        [
            longitude_representation[i] + latitude_representation[i]
            for i in range(len(longitude_representation))
        ]
    )


def binary_representation_to_geohash(binary_representation: str) -> str:
    """
    Convert the binary representation to a geohash.

    The geohash is a base32 representation of the binary representation. But it's different from the standard base32 representation.

    * Standard base32 letters: [A-Z, 2-7]
    * Geohash letters: [0-9, a-z] (excluding [a, i, l, o])

    Base32 encoding works by taking 5 bits (2^5=32) at a time and converting it to a base32 character. We will do the same here but with the geohash letters.
    Example - 1010111101110101111
    We will take 5 bits at a time and convert it to a geohash letter.
    10101 -> 21 -> b
    11101 -> 29 -> p
    11010 -> 26 -> m
    11110 -> 30 -> q (here, we are padding the last 0 to make it 5 bits)
    """
    base32_characters = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "j",
        "k",
        "m",
        "n",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
    ]
    geohash = ""
    for i in range(0, len(binary_representation), 5):
        # convert the 5 bits to a decimal number & then to a base32 character by looking up the index in the base32_characters list
        geohash += base32_characters[int(binary_representation[i : i + 5], 2)]
    return geohash


def geohash(coordinates, precision: int = 32) -> str:
    """
    Convert the latitude and longitude to a geohash.
    """
    latitude, longitude = coordinates
    longitude_representation = get_longitude_representation(longitude, precision)
    latitude_representation = get_latitude_representation(latitude, precision)
    interleaved_bits = interleave_bits(
        longitude_representation, latitude_representation
    )
    return binary_representation_to_geohash(interleaved_bits)


if __name__ == "__main__":
    budapest_coordinate = (47.4979, 19.0402)
    print(f"Geohash of Budapest: {geohash(budapest_coordinate)}")

    san_francisco_coordinate = (37.7749, -122.4194)
    print(f"Geohash of San Francisco: {geohash(san_francisco_coordinate)}")

    london_coordinate = (51.5074, -0.1278)
    print(f"Geohash of London: {geohash(london_coordinate)}")

    mumbai_coordinate = (19.076, 72.8777)
    print(f"Geohash of Mumbai: {geohash(mumbai_coordinate)}")
