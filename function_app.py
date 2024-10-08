import azure.functions as func
import os
import logging
import json
import uuid
from app_config_manager import AppConfigManager
from exchange_rates import generate_exchange_rates
from event_hub_publisher import EventHubPublisher
from blob_mover import BlobMover

app = func.FunctionApp()

app_config_manager = AppConfigManager()

@app.blob_trigger(arg_name="myblob", path=os.getenv('BLOB_PATH_FOREX_BLOB_TRIGGER'), connection="coestorageaccount01_STORAGE")
def forex_blob_trigger(myblob: func.InputStream):
    request_id = str(uuid.uuid4())
    interface_id = "INTSVC112_MOCKAPI"
    log_prefix = f"{interface_id} [{request_id}]"

    logging.info(f'{log_prefix}: Blob trigger function started processing.')

    try:
        # Retrieve cached configuration values
        config = app_config_manager.get_cached_config()
        logging.info(f'{log_prefix}: Retrieved configuration values from cache.')

        # Validate the retrieved configuration values
        if not config["event_hub_connection_string"]:
            raise ValueError(f"{log_prefix}: Event Hub connection string is not configured in Azure App Configuration.")
        
        if not config["event_hub_name"]:
            raise ValueError(f"{log_prefix}: Event Hub name is not configured in Azure App Configuration.")
        
        if not config["archive_blob_folder"]:
            raise ValueError(f"{log_prefix}: Archive blob folder is not configured in Azure App Configuration.")
        
        if not config["source_blob_folder"]:
            raise ValueError(f"{log_prefix}: Source blob folder is not configured in Azure App Configuration.")
        
        if not config["container_name"]:
            raise ValueError(f"{log_prefix}: Container name is not configured in Azure App Configuration.")
        
        if not config["storage_connection_string"]:
            raise ValueError(f"{log_prefix}: Azure Storage connection string is not configured in Azure App Configuration.")

        logging.info(f'{log_prefix}: Configuration values validated successfully.')

        # Read the contents of the blob
        blob_contents = myblob.read().decode('utf-8')
        logging.info(f'{log_prefix}: Blob contents read successfully: {blob_contents}')

        # Parse the JSON content and generate exchange rates
        try:
            exchange_rates = generate_exchange_rates(blob_contents)
            logging.info(f'{log_prefix}: Generated exchange rates: {json.dumps(exchange_rates, indent=2)}')

            # Publish exchange rates to Event Hub
            event_hub_publisher = EventHubPublisher(config["event_hub_connection_string"], config["event_hub_name"])
            event_hub_publisher.publish_messages(exchange_rates)
            logging.info(f'{log_prefix}: Successfully sent {len(exchange_rates)} messages to Event Hub.')

            # Move the blob to the archive folder
            blob_mover = BlobMover(config["storage_connection_string"])
            source_blob_name = f"{config['source_blob_folder']}/{myblob.name.split('/')[-1]}"
            target_blob_name = f"{config['archive_blob_folder']}/{myblob.name.split('/')[-1]}"
            blob_mover.move_blob(config["container_name"], source_blob_name, target_blob_name, interface_id)
            logging.info(f'{log_prefix}: Blob moved from {source_blob_name} to {target_blob_name}.')

        except json.JSONDecodeError as e:
            logging.error(f'{log_prefix}: Error parsing JSON: {e}')

    except ValueError as e:
        logging.error(f'{log_prefix}: {e}')
        raise
    except Exception as e:
        logging.error(f'{log_prefix}: Unexpected error: {e}')
        raise

    logging.info(f'{log_prefix}: Blob trigger function completed successfully.')