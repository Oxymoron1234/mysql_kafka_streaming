# Make sure to install confluent-kafka python package
# pip install confluent-kafka

import threading
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer
from config import *
from fastavro import reader
import json
import io
import time
from concurrent.futures import ThreadPoolExecutor
# Define Kafka configuration

extra_values = {
    'group.id': 'product-consumer02',
    'auto.offset.reset': 'earliest'
}
kafka_config = {**kafka_config , **extra_values}

schema_registry_client = SchemaRegistryClient({
  'url': schema_registry['url'],
  'basic.auth.user.info': '{}:{}'.format(schema_registry['api_key'], schema_registry['secret_key'])
})

# Fetch the latest Avro schema for the value
subject_name = data_contract_subject_name
schema_str = schema_registry_client.get_latest_version(subject_name).schema.schema_str

# Create Avro Deserializer for the value
key_deserializer = StringDeserializer('utf_8')
avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)

# Define the DeserializingConsumer
consumer = DeserializingConsumer({
    'bootstrap.servers': kafka_config['bootstrap.servers'],
    'security.protocol': kafka_config['security.protocol'],
    'sasl.mechanisms': kafka_config['sasl.mechanisms'],
    'sasl.username': kafka_config['sasl.username'],
    'sasl.password': kafka_config['sasl.password'],
    'key.deserializer': key_deserializer,
    'value.deserializer': avro_deserializer,
    'group.id': kafka_config['group.id'],
    'auto.offset.reset': kafka_config['auto.offset.reset'],
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 2000 # Commit every 2000 ms, i.e., every 2 seconds
})

# Subscribe to the 'retail_data' topic
topic_name = product_topic_name[0]
consumer.subscribe([topic_name])



# Deserialize Avro data
def deserialize_avro(data):
    input_data = io.BytesIO(data)
    for record in reader(input_data):
        return record

# Append data to JSON files
def append_to_json_file(record, partition):
    file_name = f'partition_{partition}.json'
    try:
        with open(file_name, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    existing_data.append(record)

    with open(file_name, 'w') as file:
        json.dump(existing_data, file, indent=4)


# Consume messages
def consume_messages(file_no):
    counter = 0
    try:
        while counter < 60 :
            msg = consumer.poll(1.0)
            if msg is None:
               counter += 1 
            elif msg.error():
                print(f"Consumer error: {msg.error()}")
                counter += 1
            else:
                print('Successfully consumed record with key {} and value {}'.format(msg.key(), msg.value()))
                record = msg.value()
                partition = msg.partition()
                #append_to_json_file(record, partition)
                append_to_json_file(record, file_no)
                counter = 0
                print(f"Appended record to partition_{file_no}.json: {record}")

    except KeyboardInterrupt:
        pass
    finally:
        print(f"process done for consumer--> {file_no}")

if __name__ == '__main__':
    with ThreadPoolExecutor() as executor:
        l = [1,2,3,4,5]
        results = executor.map(consume_messages, l)
        for result in results:
            print(result)
    consumer.close()

