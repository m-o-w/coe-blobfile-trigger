from azure.eventhub import EventHubProducerClient, EventData
import logging
import json

class EventHubPublisher:
    def __init__(self, connection_string, event_hub_name):
        self.connection_string = connection_string
        self.event_hub_name = event_hub_name
        self.client = EventHubProducerClient.from_connection_string(conn_str=self.connection_string, eventhub_name=self.event_hub_name)

    def publish_messages(self, messages):
        try:
            event_data_batch = self.client.create_batch()
            for message in messages:
                event_data_batch.add(EventData(json.dumps(message)))
            self.client.send_batch(event_data_batch)
            logging.info("Successfully sent messages to Event Hub.")
        except Exception as e:
            logging.error(f"Error sending messages to Event Hub: {e}")
