from kafka import KafkaConsumer
import json

# Initialize consumer
consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    group_id="order-processors",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

# Process messages
for message in consumer:
    order = message.value
    print(f"Processing order: {order}")
