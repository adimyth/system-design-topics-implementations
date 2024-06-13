from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# Example data
orders = [
    {"id": 1, "product": "Laptop"},
    {"id": 2, "product": "Smartphone"},
    {"id": 3, "product": "Tablet"},
    {"id": 4, "product": "Smartwatch"},
    {"id": 5, "product": "Smart TV"},
    {"id": 6, "product": "Smart Speaker"},
]
activities = [
    {"user_id": 1, "activity": "Login"},
    {"user_id": 1, "activity": "Draft Message"},
    {"user_id": 1, "activity": "Send Message"},
    {"user_id": 1, "activity": "Logout"},
    {"user_id": 2, "activity": "Login"},
    {"user_id": 2, "activity": "Logout"},
]

for i, order in enumerate(orders):
    future = producer.send("orders", value=order)
    result = future.get(timeout=60)  # Synchronous send
    print(
        f"Sent: {result.topic}, Partition: {result.partition}, Offset: {result.offset}"
    )
    time.sleep(1)

for i, activity in enumerate(activities):
    future = producer.send("user_activities", value=activity)
    result = future.get(timeout=60)  # Synchronous send
    print(
        f"Sent: {result.topic}, Partition: {result.partition}, Offset: {result.offset}"
    )
    time.sleep(1)

producer.close()
