# Rate Limiter

Properties of Rate Limiter:
1. Fast: The rate limiter should be fast and should not introduce any noticeable latency. Ex - we can't use a database to keep track of the request count as it will introduce latency.
2. Distributed: The rate limiter should be distributed and should work in a multi-server environment. Ex - we can't use local memory to keep track of the request count as it won't be shared across servers. We need a mechanism to sync the request count across all servers.
3. Configurable: The rate limiter should be configurable so that we can change the rate limit on the fly. Ex - we should be able to change the rate limit from 100 requests per minute to 200 requests per minute without restarting the server.
4. Efficient: The rate limiter should be efficient in terms of memory and CPU usage. Ex - we can't use a hash map to keep track of the request count as it will consume a lot of memory.

## Communication
We need to tell the client clearly about the rate limiting policy.
1. `429 Too Many Requests`: The server is limiting the rate at which the client can send requests.
2. `202 Accepted`: Many a time we can accept the request & add it to a queue to be processed later. In this case, we can return `202 Accepted` status code.
3. Retry-After: The server should include the time after which the client can retry the request.
4. Rate Limiting Headers: The server should include headers to tell the client about the rate limiting policy. Example - *Github* & *Twitter* have the following headers:
    - `X-RateLimit-Limit`: The maximum number of requests that the consumer is permitted to make per hour.
    - `X-RateLimit-Remaining`: The number of requests remaining in the current rate limit window.
    - `X-RateLimit-Reset`: The time at which the current rate limit window resets in UTC epoch seconds.

## Distributed Rate Limiting
1. In horizontally scalable systems, where servers come and go, it is challenging to implement rate limiting.
2. We cannot implement local rate limiting on each server, the reason being that a user can hit different servers in the cluster, and we won't be able to keep track of the total request count. Ex - assume we have 3 servers and the rate limit is 100 requests per minute, if a user hits all three servers, he can potentially make 300 requests per minute.
3. We need a mechanism to sync the request count across all servers, so that we can apply rate limiting globally.

### Sticky Sessions
One way to solve this problem is to use sticky sessions, where we tie a user's session to a specific server. This way, all requests from the user will go to the same server, and we can implement rate limiting on that server. 

However, it doesn't provide fault tolerance. If a server goes down, all users tied to that server will be affected. We will loose the request count for those users & they will be able to make more requests than the allowed limit.

### External Storage
Another way to solve this problem is to use an external storage system like Redis or Memcached to keep track of the request count per user. Here, some unique property of the user (like user id) can be used to keep track of the request count.

1. When a request comes to the server, it will increment the request count in the external storage.
2. Before serving the request, the server will check the request count in the external storage to see if the user has exceeded the rate limit.
3. If the user has exceeded the rate limit, the server will reject the request.
4. The server will also have to clean up the request count in the external storage after a certain time period.

This approach is more fault-tolerant as we are not tying a user to a specific server.

However, this approach has some drawbacks:
1. It introduces a single point of failure. If the external storage goes down, the rate limiting mechanism will stop working.
2. It introduces latency as we have to make an additional call to the external storage to check the request count.
