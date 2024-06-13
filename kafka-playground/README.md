### Create topics
Create 2 topics - `orders` & `user_activities` with 3 partitions each.

```bash
# delete topics if already exists
docker exec -it kafka kafka-topics --delete --bootstrap-server localhost:9092 --topic orders
docker exec -it kafka kafka-topics --delete --bootstrap-server localhost:9092 --topic user_activities

# create topics
docker exec -it kafka kafka-topics --create --bootstrap-server localhost:9092 --topic orders --partitions 3 --replication-factor 1
docker exec -it kafka kafka-topics --create --bootstrap-server localhost:9092 --topic user_activities --partitions 3 --replication-factor 1

# list topics
docker exec -it kafka kafka-topics --describe --topic user_activities --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --describe --topic orders --bootstrap-server localhost:9092
```