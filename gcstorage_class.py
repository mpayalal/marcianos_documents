import mimetypes
from google.cloud import storage

class GCStorage:
    def __init__(self, storage_client: storage.Client):
        self.client = storage_client
    
    def create_bucket(self, bucket_name: str, storage_class: str, bucket_location='US'):
        bucket = self.client.bucket(bucket_name)
        bucket.storage_class = storage_class
        return self.client.create_bucket(bucket, bucket_location)

    def get_bucket(self, bucket_name: str):
        return self.client.get_bucket(bucket_name)
    
    def list_buckets(self):
        buckets = self.client.list_buckets()
        return [bucket.name for bucket in buckets]
    
    def upload_file(self, bucket, blob_name, file_path):
        content_type = mimetypes.guess_type(file_path)[0]

        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path, content_type=content_type)
        return blob
    
    def upload_file_from_bytes(self, bucket, blob_name: str, file_bytes: bytes, content_type: str):
        blob = bucket.blob(blob_name)

        blob.upload_from_string(file_bytes, content_type=content_type)
        return blob
    
    def list_blobs(self, bucket_name: str, folder: str):
        return self.client.list_blobs(bucket_or_name=bucket_name, prefix=folder)
    
    def get_blob(self, bucket_name: str, blob_name: str):
        bucket = self.client.get_bucket(bucket_name)
        return bucket.get_blob(blob_name)
    
    def delete_blob(self, bucket_name: str, blob_name: str):
        blob = self.get_blob(bucket_name, blob_name)
        if blob:
            blob.delete()
            return True
        return False

    def delete_all_blobs(self, bucket_name: str):
        blobs = self.list_blobs(bucket_name)
        for blob in blobs:
            blob.delete()
        return True

    def delete_bucket(self, bucket_name: str):
        bucket = self.client.bucket(bucket_name)
        bucket.delete()
        return True
    