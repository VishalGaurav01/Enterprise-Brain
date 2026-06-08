from kafka import KafkaProducer
import json
import os
import logging

class BrainKafkaProducer:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_SERVERS", "localhost:9092")
    
    _producer = None

    @classmethod
    def get_producer(cls):
        if cls._producer is None:
            try:
                cls._producer = KafkaProducer(
                    bootstrap_servers=cls.KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    retries=5
                )
            except Exception as e:
                logging.error(f"Failed to initialize Kafka Producer: {e}")
                return None
        return cls._producer

    @classmethod
    def publish_event(cls, topic: str, event_type: str, data: dict):
        producer = cls.get_producer()
        if not producer:
            print(f"Skipping event {event_type} - Producer not available")
            return
            
        payload = {
            "event_type": event_type,
            "data": data,
            "timestamp": str(os.urandom(4).hex()) # Simplified tracking ID
        }
        
        try:
            future = producer.send(topic, payload)
            # For high reliability, we could block here or use a callback
            # future.get(timeout=10) 
            print(f"Published event {event_type} to {topic}")
        except Exception as e:
            logging.error(f"Kafka Publishing Error: {e}")

class EventBus:
    def publish_action(self, action: dict, context: dict):
        BrainKafkaProducer.publish_event('enterprise-decisions', 'business_decision_triggered', {
            "action": action,
            "context": context
        })

event_bus = EventBus()
