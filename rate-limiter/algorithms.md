## Algorithms

### Leaky Bucket Algorithm
1. We configure a bucket with a certain `bucket size` and a `process rate`.
2. When a request comes in, we check if the bucket has enough capacity to accommodate the request.
   1. If the bucket has enough capacity, we decrement the capacity by 1 and add the request to the bucket.
   2. If the bucket doesn't have enough capacity it overflows & we reject the request.
3. The bucket leaks at a constant rate. So, if the bucket is not full, it will leak at a constant rate i.e. the requests will be processed at a constant rate.

![Leaky Bucket Algorithm](https://imgur.com/xgG6TXw.png)

> Assume this is a FIFO queue. Where the requests are added to the end of the queue and removed from the front of the queue at a constant rate. If the queue is full, the request is rejected.

| Pros                             | Cons                                                    |
| -------------------------------- | ------------------------------------------------------- |
| Simple to implement              | Cannot handle burst traffic                             |
| Memory efficient                 | Difficult to get `bucket size` & `process rate` correct |
| Provides a constant request rate |                                                         |


### Token Bucket Algorithm
Similar to the Leaky Bucket Algorithm, the Token Bucket Algorithm also uses a bucket to store tokens. But, the Token Bucket Algorithm is more flexible than the Leaky Bucket Algorithm as it allows for bursty traffic.

1. We configure a bucket with a certain `bucket size` and a `process rate`.
2. We add tokens to the bucket at a constant rate.
3. When a request comes in, we check if the bucket has enough tokens to accommodate the request.
   1. If the bucket has enough tokens, we decrement the tokens by 1 and process the request.
   2. If the bucket doesn't have enough tokens, we reject the request.
4. The bucket can store a maximum of `bucket size` tokens. If the bucket is full, the tokens are discarded.

> 🔥 Note that this doesn't take into account the input rate possible for the downstream service. If the downstream service can only handle a certain number of requests per second & our bucket has enough tokens to accommodate all the requests, we can still end up overwhelming the downstream service. This is different to leaky bucket algorithm where if we know the max ingestion capacity of the downstream service, we can always prevent it from being overwhelmed

### Sliding Window Log Algorithm