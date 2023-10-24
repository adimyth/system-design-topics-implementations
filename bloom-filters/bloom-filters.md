Bloom filters are a probabilistic data structure used to test whether an element is a member of a set. They can have false positives, but they guarantee no false negatives. This means that when a Bloom filter tells you an item is not in the set, you can be sure it's not; but if it says it is in the set, there's a chance it might be wrong.

Let's break down the implementation and your questions:

### Implementation:

1. **Bit Array**: At the heart of a Bloom filter is a bit array, typically initialized with all bits set to 0. The size of this bit array determines the space the Bloom filter uses in memory.

2. **Hash Functions**: A Bloom filter uses multiple (k) hash functions. Each hash function will take an input (the item you're checking or adding to the filter) and produce an index in the bit array.

3. **Adding an Item**: When you want to add an item to the Bloom filter, you pass it through each of the k hash functions to get k indexes. You then set the bits at each of these k positions in the bit array to 1.

4. **Checking an Item**: To check if an item is in the set, you again pass it through the k hash functions to get k indexes. If any of the bits at these k positions is 0, you can be sure the item is not in the set. If all are 1, the item might be in the set (or it might be a false positive).

### Accuracy by Increasing Space:

The probability of a false positive in a Bloom filter is determined by:
- Size of the bit array (m)
- Number of hash functions (k)
- Number of items in the filter (n)

If you increase the size of the bit array (m) while keeping the number of items (n) constant, the probability of a false positive decreases. However, if you keep increasing the number of items added to the filter without increasing the size of the bit array, the probability of false positives will increase.

An optimal number of hash functions (k) in relation to the size of the bit array and the number of items can be calculated to minimize the false positive probability. The formula is:

```
k = (m/n) * ln(2)
```

### Explanations:
https://www.youtube.com/watch?v=V3pzxngeLqw

### Additional Improvements
1. **Dynamic Resizing**: A production-ready Bloom filter might support dynamic resizing. As more elements are added, the false positive rate increases. To handle this, the filter could be resized, and elements rehashed.

2. **Optimal Hash Function Count**: The number of hash functions (k) impacts the false positive rate. Currently, we have used a fixed number of hash functions (2).

3. **Counting Bloom Filters**: Counting Bloom filters are an extension that allows deletions. Instead of a bit array, they use an array of counters. This is useful when it's important to be able to remove elements from the filter.

4. **Storage Efficiency**: _The provided implementation uses a Python list of integers (which are each 0 or 1). This is not space-efficient. A production Bloom filter might use actual bit manipulation to store and manipulate the filter in true binary format, which would be much more space-efficient._

5. **Persistence**: Some applications might require the Bloom filter to be saved and restored, which would require serialization and deserialization methods.
