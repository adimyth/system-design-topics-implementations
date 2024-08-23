from typing import Tuple


def geohash_to_binary_representation(geohash: str) -> str:
    """
    Convert the geohash to a binary representation.

    The geohash is a string of alternating bits. The first bit represents the longitude and the second bit represents the latitude.

    The geohash is a base32 representation of the binary representation. But it's different from the standard base32 representation.

    * Standard base32 letters: [A-Z, 2-7]
    * Geohash letters: [0-9, a-z] (excluding [a, i, l, o])

    We will lookup a dictionary to find the binary representation of each geohash letter and concatenate them to get the binary representation.
    """
    geohash_to_binary = {
        "0": "00000",
        "1": "00001",
        "2": "00010",
        "3": "00011",
        "4": "00100",
        "5": "00101",
        "6": "00110",
        "7": "00111",
        "8": "01000",
        "9": "01001",
        "b": "01010",
        "c": "01011",
        "d": "01100",
        "e": "01101",
        "f": "01110",
        "g": "01111",
        "h": "10000",
        "j": "10001",
        "k": "10010",
        "m": "10011",
        "n": "10100",
        "p": "10101",
        "q": "10110",
        "r": "10111",
        "s": "11000",
        "t": "11001",
        "u": "11010",
        "v": "11011",
        "w": "11100",
        "x": "11101",
        "y": "11110",
        "z": "11111",
    }

    binary_representation = ""
    for letter in geohash:
        binary_representation += geohash_to_binary[letter]
    return binary_representation


def segregate_latitude_and_longitude_representation(
    binary_representation: str,
) -> Tuple[str, str]:
    """
    The geohash is a string of alternating bits. The first bit represents the longitude and the second bit represents the latitude. We will segregate the binary representation into two parts - one for longitude and one for latitude.

    In the binary representation, the first bit represents the longitude and the second bit represents the latitude. So, we will take every alternate bit to get the longitude and latitude representation.

    But since for geohash 32 bit encoding, we group 5 bits together to get a geohash letter, our input binary representation will be a multiple of 5 i.e 65 bits.

    How do we discard the additional 1 bit?
    """
    longitude_representation = ""
    latitude_representation = ""
    for i in range(0, len(binary_representation) - 3, 2):
        longitude_representation += binary_representation[i]
        latitude_representation += binary_representation[i + 1]
    # Hack for discarding the additional 1 bit
    longitude_representation += binary_representation[-2]
    latitude_representation += binary_representation[-1]
    return longitude_representation, latitude_representation


def reverse_longitude_representation(longitude_representation: str) -> float:
    """
    Convert the binary representation of longitude to a float in range [-180, 180].
    """
    # convert the binary representation to a decimal value
    decimal_value = int(longitude_representation, 2)
    # maximum value of 32 bit integer (4294967295)
    max_value = 2**32 - 1
    # normalize the decimal value to the range [0, 4294967295]
    normalized_longitude = decimal_value / max_value
    # scale the normalized value to the total range of longitude [-180, 180] i.e 360
    normalized_longitude = normalized_longitude * 360
    # shift the value to the range [-180, 180]
    longitude = normalized_longitude - 180
    return round(longitude, 4)


def reverse_latitude_representation(latitude_representation: str) -> float:
    """
    Convert the binary representation of latitude to a float in range [-90, 90].
    """
    decimal_value = int(latitude_representation, 2)
    max_value = 2**32 - 1
    latitude = (decimal_value / max_value) * 180 - 90
    return round(latitude, 4)


def reverse_geohash(geohash: str) -> Tuple[float, float]:
    """
    Convert the geohash to latitude and longitude.
    """
    binary_representation = geohash_to_binary_representation(geohash)
    longitude_representation, latitude_representation = (
        segregate_latitude_and_longitude_representation(binary_representation)
    )
    longitude = reverse_longitude_representation(longitude_representation)
    latitude = reverse_latitude_representation(latitude_representation)
    return latitude, longitude


if __name__ == "__main__":
    budapest_geohash_representation = "u2mw1q8xkf61e"
    latitude, longitude = reverse_geohash(budapest_geohash_representation)
    print(f"Budapest: ({latitude}, {longitude})")

    san_francisco_geohash_representation = "9q8yyk8ytpxr4"
    latitude, longitude = reverse_geohash(san_francisco_geohash_representation)
    print(f"San Francisco: ({latitude}, {longitude})")

    london_geohash_representation = "gcpvj0duq5338"
    latitude, longitude = reverse_geohash(london_geohash_representation)
    print(f"London: ({latitude}, {longitude})")

    mumbai_geohash_representation = "te7ud2evv2pu1"
    latitude, longitude = reverse_geohash(mumbai_geohash_representation)
    print(f"Mumbai: ({latitude}, {longitude})")
