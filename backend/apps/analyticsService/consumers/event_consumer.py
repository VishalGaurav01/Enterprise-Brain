from kafka import KafkaConsumer, KafkaProducer
import json
import os
import logging

class AnalyticsEventConsumer:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_SERVERS", "localhost:9092")
    TOPICS = ["employee-events", "project-events", "finance-events"]
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            *self.TOPICS,
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            group_id="analytics_service_group",
            auto_offset_reset='earliest',
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        self.producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"Analytics Consumer standing by for topics: {self.TOPICS}")

    def start_listening(self):
        for message in self.consumer:
            event = message.value
            retry_count = event.get("retry_count", 0)
            
            try:
                self.process_event(event)
            except Exception as e:
                logging.error(f"Processing failed for {event.get('event_type')}: {e}")
                if retry_count < 3:
                    self.retry_message(message.topic, event, retry_count)
                else:
                    self.send_to_dlq(message.topic, event)

    def process_event(self, event):
        event_type = event.get("event_type")
        data = event.get("data")
        if event_type == "EMPLOYEE_CREATED":
            self.handle_employee_created(data)
        elif event_type == "PROJECT_CREATED":
            self.handle_project_created(data)

    def retry_message(self, topic, event, retry_count):
        event["retry_count"] = retry_count + 1
        print(f"Retrying message... attempt {event['retry_count']}")
        self.producer.send(topic, event)

    def send_to_dlq(self, topic, event):
        dlq_topic = f"{topic}-dlq"
        print(f"CRITICAL: Sending message to DLQ: {dlq_topic}")
        self.producer.send(dlq_topic, event)

    def handle_employee_created(self, data):
        # Implementation for updating analytics DB or KPI snapshots
        print(f"Recording metrics for new employee: {data.get('employee_id')}")

    def handle_project_created(self, data):
        # Implementation for updating project dashboard data
        print(f"Initializing dashboard for project: {data.get('name')}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = AnalyticsEventConsumer()
    consumer.start_listening()
