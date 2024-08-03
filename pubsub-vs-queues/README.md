# PubSub vs Queues

## Kafka vs Redis
| Kafka                                                                                                  | Redis                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Scales horizontally                                                                                    | Scales vertically                                                                                                                                                                 |
| Persistent (on disk)                                                                                   | In-memory                                                                                                                                                                         |
| Recovery from crashes as it persists data on disk & replicates data across cluster for fault tolerance | Redis's durability is more limited when used as a Pub/Sub system because messages are not persisted after delivery. Redis Streams offer some sort of durability, but not the best |
| High throughput                                                                                        | Low latency                                                                                                                                                                       |
| Ordered messages  - messages are received by the consumer in the same order that they were produced    | No guarantee - It doesn't matter the order in which the messages are consumed                                                                                                     |
| At-least-once                                                                                          | At-most-once                                                                                                                                                                      |
| Kafka is difficult to setup and maintain                                                               | Redis is easier to setup and maintain                                                                                                                                             |

* The amount of events that Kafka can handle is much higher than Redis. Since all the events in Redis are stored in memory, the number of events that can be stored is limited by the amount of memory available.
* On the other hand, Kafka can store events on disk, which allows it to store a much larger number of events.
* Also, in case of a crash, Kafka can recover the events from disk, while Redis will lose all the events that were not consumed by the subscribers.
* Redis is a good choice when you need low latency and you don't need to store a large number of events.