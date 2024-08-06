import os
import azure.functions as func
import logging
import re
import json
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential
from azure.appconfiguration import AzureAppConfigurationClient

app = func.FunctionApp()

# Initialize Azure App Configuration client
credential = DefaultAzureCredential()
app_config_client = AzureAppConfigurationClient.from_connection_string(os.getenv("APP_CONFIG_CONNECTION_STRING"))

# Fetch the Event Hub connection string from App Configuration
config_setting = app_config_client.get_configuration_setting(key="EventHubConnectionString_FOREX_BLOB_TRIGGER")
EVENT_HUB_CONNECTION_STR = config_setting.value
EVENT_HUB_NAME = "coe-eventhub-01"

@app.function_name(name="BlobTrigger1")
@app.blob_trigger(arg_name="myblob", path="defaultcontainer2/inbound/{name}.json",
                  connection="coestorageaccount01_STORAGE")
def forex_file_trigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                 f"Name: {myblob.name}, "
                 f"Blob Size: {myblob.length} bytes")

    contents = myblob.read().decode('utf-8')

    if validate_blob(myblob.name, contents):
        logging.info(f"Valid file received for processing: "
                     f"Name: {myblob.name}, "
                     f"Blob Size: {myblob.length} bytes")
        logging.info(f"Blob contents: {contents[:1000]}")  # Log the first 1000 characters
        exchange_rates = generate_exchange_rates(contents)
        logging.info(f"Generated exchange rates: {json.dumps(exchange_rates, indent=2)}")
        publish_to_event_hub(exchange_rates)
    else:
        logging.error(f"Validation failed for blob: {myblob.name}")

def validate_blob(blob_name: str, contents: str) -> bool:
    # Validate file contents are not null
    if not contents:
        logging.error(f"File contents are null: {blob_name}")
        return False
    return True

def generate_exchange_rates(json_content: str) -> list:
    data = json.loads(json_content)
    base_currency = data['source']
    quotes = data['quotes']
    timestamp = data['timestamp']

    exchange_rates = []

    # Calculate exchange rates between all possible currency pairs
    for from_currency, from_rate in quotes.items():
        from_currency = from_currency[len(base_currency):]  # Extract target currency from key
        for to_currency, to_rate in quotes.items():
            to_currency = to_currency[len(base_currency):]  # Extract target currency from key
            if from_currency != to_currency:
                rate = (1 / from_rate) * to_rate
                exchange_rates.append({
                    "base_currency": from_currency,
                    "target_currency": to_currency,
                    "date": timestamp,
                    "exchange_rate": rate
                })

    return exchange_rates

def publish_to_event_hub(exchange_rates: list):
    try:
        producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENT_HUB_NAME)
        event_data_batch = producer.create_batch()

        for rate in exchange_rates:
            event_data_batch.add(EventData(json.dumps(rate)))

        producer.send_batch(event_data_batch)
        logging.info("Exchange rates published to Event Hub")
    except Exception as e:
        logging.error(f"Failed to publish exchange rates: {e}")
    finally:
        producer.close()
