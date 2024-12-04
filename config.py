
#Please place your schema api key file and bootstrap key file in the same directory and provide there name in line no 3,4 respectively like below given example
schema_file_path = 'api-key-B5OCH6TADT2Z5G5W.txt'
bootstrap_file_path = "api-key-7IAK4M6LTPU3LXG7.txt"
# Read the file
with open(schema_file_path, 'r') as file:
    content = file.read().strip()  # Read content and remove any surrounding whitespace
    schema_api_key = content.split('API key:')[1].split('\n')[1]
    schema_secret = content.split('API secret:')[1].split('\n')[1]
    print(schema_api_key)
    print(schema_secret)

with open(bootstrap_file_path, 'r') as file:
    content = file.read().strip()  
    bootstrap_api_key = content.split('API key:')[1].split('\n')[1]
    bootstrap_secret = content.split('API secret:')[1].split('\n')[1]
    bootstrap_uri = content.split('Bootstrap server:')[1].split('\n')[1]


data_contract_subject_name = 'product_update-value'
product_topic_name='product_update', 

schema_registry = {
    'url' : "https://psrc-5j7x8.us-central1.gcp.confluent.cloud",
    "api_key":schema_api_key,
    "secret_key":schema_secret
}
kafka_config = {
    'bootstrap.servers': bootstrap_uri,
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': bootstrap_api_key,
    'sasl.password': bootstrap_secret
}

mysql_config = {
    "host":"localhost",
    "user":"root",
    "password":"root_password",
    "database":"BuyOnline"
}


