# Make sure to install confluent-kafka python package
# pip install confluent-kafka

import datetime
from datetime import datetime
import threading
from decimal import *
from time import sleep
from uuid import uuid4, UUID
import time
import mysql.connector
from config import *
import math
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.

    Args:
        err (KafkaError): The error that occurred on None on success.

        msg (Message): The message that was produced or failed.

    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.

    """
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))
    print("=====================")

# Create a Schema Registry client and fetch those creds from config
s_url = schema_registry['url']
s_api_key = schema_registry['api_key']
s_secret = schema_registry['secret_key']
schema_registry_client = SchemaRegistryClient({
  'url': s_url,
  'basic.auth.user.info': '{}:{}'.format(s_api_key, s_secret)
})

# Fetch the latest Avro schema for the value
subject_name = data_contract_subject_name
schema_str = schema_registry_client.get_latest_version(subject_name).schema.schema_str
print("Schema from Registery---")
print(schema_str)
print("=====================")

# Create Avro Serializer for the value
key_serializer = StringSerializer('utf_8')
avro_serializer = AvroSerializer(schema_registry_client, schema_str)

# Define the SerializingProducer
producer = SerializingProducer({
    'bootstrap.servers': kafka_config['bootstrap.servers'],
    'security.protocol': kafka_config['security.protocol'],
    'sasl.mechanisms': kafka_config['sasl.mechanisms'],
    'sasl.username': kafka_config['sasl.username'],
    'sasl.password': kafka_config['sasl.password'],
    'key.serializer': key_serializer,  # Key will be serialized as a string
    'value.serializer': avro_serializer  # Value will be serialized as Avro
})

def fetch_data(last_updated):
    rows = ""
    try:
        connection = mysql.connector.connect(
            host = mysql_config['host'], 
            user = mysql_config['user'], 
            password = mysql_config['password'],
            database = mysql_config['database']
        )
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM products WHERE updated_timestamp > %s"
        cursor.execute(query, (last_updated,))
        rows = cursor.fetchall()
    except Exception as e:
        print (f"Error ---- {e}")
    finally:
        cursor.close()
        connection.close()
    return rows

#fetch last record time stamp
def fetch_last_update():
    rows = ""
    try:
        connection = mysql.connector.connect(
            host = mysql_config['host'], 
            user = mysql_config['user'], 
            password = mysql_config['password'],
            database = mysql_config['database']
        )
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM products ORDER BY updated_timestamp DESC LIMIT 1"
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print (row)
            last_updatetimestamp = row['updated_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print (f"Error ---- {e}")
        current_time = datetime.now()
        # Format it to match MySQL TIMESTAMP format (YYYY-MM-DD HH:MM:SS)
        last_updatetimestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
    finally:
        cursor.close()
        connection.close()
    return last_updatetimestamp

#convert price doller to inr and apply gst 
def convert_price_doller(catalog, price_doller):
    price_in_inr = price_doller*88
    if (catalog == 'Electronics') or (catalog == 'Home'):
        price_in_inr *= 1.18 
    if (catalog == 'Clothing') or (catalog == 'Book'):
        price_in_inr *= 1.12
    if catalog == 'Toy':
        price_in_inr *= 1.28 
    else:
        price_in_inr *= 1.18 
    price_in_inr = math.floor(price_in_inr * 100) / 100
    return price_in_inr


# Produce messages
def produce_messages():
    last_updated = fetch_last_update()
    time.sleep(5)
    while True:
        records = fetch_data(last_updated)
        if not records:
            break
        topic_name = product_topic_name[0]
        for record in records:
            index = record['product_id']
            data = {}
            data['product_id'] = record['product_id']
            data['product_name'] = record['name']
            data['category'] = record['category']
            data['price'] = convert_price_doller(record['category'] , float(record['price']))
            data['updated_timestamp'] = record['updated_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"processing id no {record['product_id']}  with record {data}")
            producer.produce(
            topic=topic_name, 
            key=str(index), 
            value=data, 
            on_delivery=delivery_report
            )
        producer.flush()
        time.sleep(5)
        current_time = datetime.now()
        # Format it to match MySQL TIMESTAMP format (YYYY-MM-DD HH:MM:SS)
        last_updated = current_time.strftime('%Y-%m-%d %H:%M:%S')
        last_updated = record['updated_timestamp']
        

if __name__ == '__main__':
    produce_messages()
    print("All Data successfully published to Kafka")