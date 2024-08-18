from azure.storage.blob import BlobServiceClient
import logging

class BlobMover:
    def __init__(self, storage_connection_string):
        self.blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

    def move_blob(self, container_name, source_blob_name, target_blob_name, interface_id):
        try:
            logging.info(f"[{interface_id}] Attempting to move blob {source_blob_name} to {target_blob_name}")
            source_blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=source_blob_name)
            target_blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=target_blob_name)

            target_blob_client.start_copy_from_url(source_blob_client.url)
            source_blob_client.delete_blob()
            logging.info(f"[{interface_id}] Moved blob {source_blob_name} to archive {target_blob_name}")
        except Exception as e:
            logging.error(f"[{interface_id}] Error moving blob: {e}")
            raise