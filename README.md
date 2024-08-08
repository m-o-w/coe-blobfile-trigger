# Azure Function for Blob Trigger and Event Hub Publishing

This project implements an Azure Function that triggers on new blobs uploaded to a specified Azure Blob Storage container. It processes the JSON content of the blob to generate exchange rates between various currency pairs based on a base currency, and then publishes these exchange rates to an Azure Event Hub.

## Project Structure

- `app_config_manager.py`: Handles retrieval of configuration values from Azure App Configuration.
- `exchange_rates.py`: Contains the logic to generate exchange rates from the JSON content of the blob.
- `event_hub_publisher.py`: Manages the publishing of messages to Azure Event Hub.
- `__init__.py`: The main Azure Function that triggers on blob upload, processes the blob content, and publishes exchange rates to Event Hub.
- `function.json`: Configuration for the Azure Function trigger.
- `requirements.txt`: Lists all dependencies for the project.

## Environmental Variables

Ensure the following environment variables are set in your Azure Function App settings:

- `AZURE_APP_CONFIG_CONNECTION_STRING`: The connection string for your Azure App Configuration.
  - Example: `Endpoint=https://<your-app-config-name>.azconfig.io;Id=<id>;Secret=<secret>`
- `BLOB_PATH_FOREX_BLOB_TRIGGER`: The path to the blob storage container to monitor.
  - Example: `defaultcontainer2/inbound/{name}`

## Azure App Configuration Variables

Add the following variables to your Azure App Configuration:

- `EventHubConnectionString_FOREX_BLOB_TRIGGER`: The connection string for your Azure Event Hub.
  - Example: `Endpoint=sb://<your-event-hub-namespace>.servicebus.windows.net/;SharedAccessKeyName=<key-name>;SharedAccessKey=<key>`
- `EventHubName_FOREX_EVENTHUB_TRIGGER`: The name of your Azure Event Hub.
  - Example: `forex-eventhub`

## How It Works

1. **Blob Trigger**: The Azure Function is triggered whenever a new blob is uploaded to the specified container.
2. **Process Blob Content**: The function reads and parses the JSON content of the blob.
3. **Generate Exchange Rates**: Using the base currency and quotes from the JSON content, it generates exchange rates between all possible currency pairs.
4. **Publish to Event Hub**: The generated exchange rates are published to the specified Azure Event Hub.

## Dependencies

Ensure you have the following dependencies listed in `requirements.txt`:

