from kafka import KafkaConsumer
import json

# Initialize consumer
consumer = KafkaConsumer(
    "user_activities",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    group_id="user-activity-processors",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

# Process messages
for message in consumer:
    order = message.value
    print(f"Processing order: {order}")
