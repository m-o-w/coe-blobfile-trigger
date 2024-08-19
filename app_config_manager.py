from azure.appconfiguration import AzureAppConfigurationClient
import os
import logging

class AppConfigManager:
    def __init__(self):
        self.connection_string = os.getenv('AZURE_APP_CONFIG_CONNECTION_STRING')
        if not self.connection_string:
            raise ValueError("Azure App Configuration connection string is not set in environment variables.")
        self.client = AzureAppConfigurationClient.from_connection_string(self.connection_string)
        self.cached_config = None

    def get_configuration_value(self, key):
        try:
            config_setting = self.client.get_configuration_setting(key=key)
            return config_setting.value
        except Exception as e:
            logging.error(f"Error retrieving configuration value for key {key}: {e}")
            return None

    def get_cached_config(self):
        if self.cached_config is None:
            self.cached_config = {
                "event_hub_connection_string": self.get_configuration_value("EventHubConnectionString_FOREX_BLOB_TRIGGER"),
                "event_hub_name": self.get_configuration_value("EventHubName_FOREX_EVENTHUB_TRIGGER"),
                "archive_blob_folder": self.get_configuration_value("ArchiveBlobFolder_FOREX_BLOB_TRIGGER"),
                "source_blob_folder": self.get_configuration_value("SourceBlobFolder_FOREX_BLOB_TRIGGER"),
                "container_name": self.get_configuration_value("ContainerName_FOREX_BLOB_TRIGGER"),
                "storage_connection_string": self.get_configuration_value("AZURE_STORAGE_CONNECTION_STRING")
            }
        return self.cached_config

# Usage example
if __name__ == "__main__":
    try:
        app_config_manager = AppConfigManager()
        config = app_config_manager.get_cached_config()
        print(config)
    except ValueError as e:
        print(e)