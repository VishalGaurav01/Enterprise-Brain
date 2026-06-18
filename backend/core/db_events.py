from sqlalchemy import event
from core.config import Base
from apps.shared.kafka_producer import BrainKafkaProducer
import json
import decimal
import datetime
from uuid import UUID

def serialize_value(val):
    if isinstance(val, UUID):
        return str(val)
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.isoformat()
    if isinstance(val, decimal.Decimal):
        return float(val)
    return val

def object_to_dict(obj):
    return {c.name: serialize_value(getattr(obj, c.name)) for c in obj.__table__.columns}

def after_insert_listener(mapper, connection, target):
    table_name = target.__table__.name
    data = object_to_dict(target)
    BrainKafkaProducer.publish_event('db.events', f'{table_name}_inserted', {
        'table': table_name,
        'operation': 'insert',
        'data': data
    })

def after_update_listener(mapper, connection, target):
    table_name = target.__table__.name
    data = object_to_dict(target)
    BrainKafkaProducer.publish_event('db.events', f'{table_name}_updated', {
        'table': table_name,
        'operation': 'update',
        'data': data
    })

def after_delete_listener(mapper, connection, target):
    table_name = target.__table__.name
    data = object_to_dict(target)
    BrainKafkaProducer.publish_event('db.events', f'{table_name}_deleted', {
        'table': table_name,
        'operation': 'delete',
        'data': data
    })

def setup_db_events():
    event.listen(Base, 'after_insert', after_insert_listener, propagate=True)
    event.listen(Base, 'after_update', after_update_listener, propagate=True)
    event.listen(Base, 'after_delete', after_delete_listener, propagate=True)
    print("Database event listeners attached successfully.")
