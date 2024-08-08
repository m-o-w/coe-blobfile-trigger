from azure.appconfiguration import AzureAppConfigurationClient
import os
import logging

class AppConfigManager:
    def __init__(self):
        self.connection_string = os.getenv('AZURE_APP_CONFIG_CONNECTION_STRING')
        if not self.connection_string:
            raise ValueError("Azure App Configuration connection string is not set in environment variables.")
        self.client = AzureAppConfigurationClient.from_connection_string(self.connection_string)

    def get_configuration_value(self, key):
        try:
            config_setting = self.client.get_configuration_setting(key=key)
            return config_setting.value
        except Exception as e:
            logging.error(f"Error retrieving configuration value for key {key}: {e}")
            return None

# Usage example
if __name__ == "__main__":
    try:
        app_config_manager = AppConfigManager()
        event_hub_connection_string = app_config_manager.get_configuration_value("EventHubConnectionString_FOREX_BLOB_TRIGGER")
        print(event_hub_connection_string)
    except ValueError as e:
        print(e)
