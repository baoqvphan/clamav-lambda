import boto3
import json
from botocore.exceptions import ClientError
from app.core.logging_config import LoggerHelper
import app.core.app_config as app_config


logger = LoggerHelper.get_logger(__name__)

class SqsService:
    """
    AWS SQS service that interacts with Amazon Simple Queue Service (SQS) for sending events.
    """

    def __init__(self):
        """
        Initializes the SQS client with the region and queue URL from the app configuration.
        """
        try:
            self.sqs_client = boto3.client("sqs", region_name=app_config.AWS_REGION)
            logger.info(f"SQS client initialized for region: {app_config.AWS_REGION}")
        except ClientError as e:
            logger.error(f"Failed to initialize SQS client: {e}")
            raise

    async def send_event(self, message: dict) -> bool:
        """
        Sends an event to the SQS queue.
        """
        try:
            message_body = json.dumps(message)
            response = self.sqs_client.send_message(
                QueueUrl=app_config.SQS_QUEUE_URL,
                MessageBody=message_body
            )
            logger.info(f"Message sent successfully to SQS. Message ID: {response.get('MessageId')}")
            return True
        except ClientError as e:
            logger.error(f"ClientError occurred while sending message to SQS: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error occurred while sending message to SQS: {e}")
            return False
