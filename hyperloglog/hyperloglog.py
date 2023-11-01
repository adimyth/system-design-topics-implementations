import hashlib
import math


class HyperLogLog:
    def __init__(self, p):
        self.p = p
        self.m = 2**p
        self.buckets = [0] * self.m

    def add(self, item):
        hashed_val = int(hashlib.md5(str(item).encode()).hexdigest(), 16)
        bucket = hashed_val & (self.m - 1)  # Get the last p bits
        leading_zeros = self._count_leading_zeros(hashed_val >> self.p)
        self.buckets[bucket] = max(self.buckets[bucket], leading_zeros)

    def _count_leading_zeros(self, num):
        if num == 0:
            return 32
        count = 0
        while (num & 1) == 0:
            count += 1
            num >>= 1
        return count

    def estimate(self):
        inverse_sum = sum([2**-bucket for bucket in self.buckets])
        return self.m**2 * (1 / inverse_sum)


# Testing
hll = HyperLogLog(6)
for i in range(100000):
    hll.add(str(i))
print(hll.estimate())  # Should be close to 1000
