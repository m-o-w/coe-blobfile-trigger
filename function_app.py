import azure.functions as func
import os
import logging
import json
from app_config_manager import AppConfigManager  # Assuming your class is in a file named app_config_manager.py
from exchange_rates import generate_exchange_rates  # Assuming your method is in a file named exchange_rates.py
from event_hub_publisher import EventHubPublisher  # Assuming your class is in a file named event_hub_publisher.py

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path=os.getenv('BLOB_PATH_FOREX_BLOB_TRIGGER'), connection="coestorageaccount01_STORAGE")
def forex_blob_trigger(myblob: func.InputStream):
    logging.info(f"Processing blob Name: {myblob.name}")
    
    try:
        # Set up AppConfigManager with the connection string from environment variable
        app_config_manager = AppConfigManager()

        # Retrieve the Event Hub connection string and name from Azure App Configuration
        event_hub_connection_string = app_config_manager.get_configuration_value("EventHubConnectionString_FOREX_BLOB_TRIGGER")
        event_hub_name = app_config_manager.get_configuration_value("EventHubName_FOREX_EVENTHUB_TRIGGER")
        
        if not event_hub_connection_string:
            raise ValueError("Event Hub connection string is not configured in Azure App Configuration.")
        
        if not event_hub_name:
            raise ValueError("Event Hub name is not configured in Azure App Configuration.")

        # Read the contents of the blob
        blob_contents = myblob.read().decode('utf-8')
        logging.info(f"Blob contents: {blob_contents}")

        # Parse the JSON content and generate exchange rates
        try:
            exchange_rates = generate_exchange_rates(blob_contents)
            logging.info(f"Generated exchange rates: {json.dumps(exchange_rates, indent=2)}")
            
            # Publish exchange rates to Event Hub
            event_hub_publisher = EventHubPublisher(event_hub_connection_string, event_hub_name)
            event_hub_publisher.publish_messages(exchange_rates)
            logging.info(f"Successfully sent {len(exchange_rates)} messages to Event Hub.")

        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON: {e}")

    except ValueError as e:
        logging.error(e)
        raise
