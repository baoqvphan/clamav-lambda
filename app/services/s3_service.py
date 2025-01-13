import boto3
import csv
import io
import os
from botocore.exceptions import ClientError
from app.core.logging_config import LoggerHelper
import app.core.app_config as app_config


logger = LoggerHelper.get_logger(__name__)

class S3Service:
    """
    AWS S3 service to interact with S3 buckets and objects.
    Provides methods for downloading files, adding tags, and fetching CSV content.
    """
    def __init__(self):
        """
        Initializes the S3Service by creating an S3 client using Boto3.
        The client is configured for the specified AWS region.
        """
        try:
            self.s3_client = boto3.client("s3", region_name=app_config.AWS_REGION)
            logger.info(f"S3 client initialized for region: {app_config.AWS_REGION}")
        except (ValueError, ClientError) as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def put_tags(self, bucket_name: str, object_key: str, new_tags: dict = {}) -> None:
        """
        Adds or updates tags on a specified S3 object.
        
        Args:
            bucket_name (str): The name of the S3 bucket.
            object_key (str): The key (path) of the S3 object.
            new_tags (dict): A dictionary of tags to be added or updated.
        """
        logger.info(f"Adding tags to object {object_key} in bucket {bucket_name}: {new_tags}")
        try:
            # Fetch existing tags
            response = self.s3_client.get_object_tagging(Bucket=bucket_name, Key=object_key)
            old_tags = {tag["Key"]: tag["Value"] for tag in response["TagSet"]}

            # Combine existing tags with the new ones
            tags = {**old_tags, **new_tags}

            # Update tags on the S3 object
            self.s3_client.put_object_tagging(
                Bucket=bucket_name,
                Key=object_key,
                Tagging={"TagSet": [{"Key": str(k), "Value": str(v)} for k, v in tags.items()]}
            )
            logger.info("Tags were successfully added/updated.")
        
        except ClientError as e:
            logger.error(f"Error occurred while adding/updating tags for '{object_key}' in bucket '{bucket_name}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")

    def download_s3_file(self, bucket: str, object_key: str, to_path: str) -> None:
        """
        Downloads a file from S3 to a local path.

        Args:
            bucket (str): The name of the S3 bucket.
            object_key (str): The key (path) of the S3 object.
            to_path (str): The local path where the file should be downloaded.
        """
        logger.info(f"Starting download of file '{object_key}' from S3 bucket '{bucket}' to local path '{to_path}'")
        try:
            self.s3_client.download_file(bucket, object_key, to_path)
            file_size = os.path.getsize(to_path) / (1024 * 1024)  # Size in MB
            logger.info(f"File {object_key} ({file_size:.2f} MB) has been downloaded successfully to '{to_path}'.")

        except ClientError as e:
            logger.error(f"Error downloading file '{object_key}' from S3 bucket '{bucket}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
