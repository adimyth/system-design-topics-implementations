import hashlib


class BloomFilter:
    def __init__(self, size, hash_functions):
        self.size = size
        # In actual implementation, we would use a bit array instead of a list of integers.
        self.bit_array = [0] * size
        self.hash_functions = hash_functions

    def add(self, item):
        for hf in self.hash_functions:
            position = hf(item) % self.size
            self.bit_array[position] = 1

    def might_contain(self, item):
        for hf in self.hash_functions:
            position = hf(item) % self.size
            if self.bit_array[position] == 0:
                return False
        return True


# Let's define two simple hash functions using hashlib
def hash1(item):
    return int(hashlib.md5(item.encode()).hexdigest(), 16)


def hash2(item):
    return int(hashlib.sha256(item.encode()).hexdigest(), 16)


# Testing our Bloom Filter
bf = BloomFilter(1000, [hash1, hash2])

items_to_add = ["apple", "banana", "cherry"]
for item in items_to_add:
    bf.add(item)

# Check items
for item in ["apple", "banana", "cherry", "date", "fig"]:
    print(f"Is {item} in the set? {'Yes' if bf.might_contain(item) else 'No'}")
