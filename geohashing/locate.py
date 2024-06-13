from typing import List


def geohash_generator(precision: int) -> List[str]:
    """
    Generate all possible geohashes of a given precision
    """
    geohash_characters = [
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
    geohash_list = []
    # for the precision of 1, there are 32 possible geohashes, for precision of 2, there are 1024 possible geohashes and so on, generate this automatically for the given value of precision
    for i in range(32**precision):
        geohash = ""
        for j in range(precision):
            geohash += geohash_characters[(i // (32**j)) % 32]
        geohash_list.append(geohash)
    return geohash_list


def locate(geohash_list: List[str], search_geohash: str, radius: int) -> List[str]:
    """
    Returns all the adjacent geohashes (grids) of a given geohash within a given radius using prefix matching.
    """
    # 1. Do a range precision lookup - {{1: "min": 5000, "max": 5000}, {2: "min": 1250, "max": 624}, ...}
    # 2. Find the precision level to lookup based on the radius.
    # 3. Find the geohashes to lookup based on the search_geohash and the precision level by prefix matching the geohash characters upto the precision level.
    pass
