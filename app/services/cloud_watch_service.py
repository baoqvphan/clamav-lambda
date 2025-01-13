import boto3
from botocore.exceptions import ClientError
from app.core.logging_config import LoggerHelper
import app.core.app_config as app_config


logger = LoggerHelper.get_logger(__name__)

class CloudWatchService:
    """
    AWS CloudWatch service for publishing custom metrics to CloudWatch.
    Provides methods for creating a CloudWatch client and publishing metrics.
    """
    def __init__(self, namespace: str):
        """
        Initializes the CloudWatchService by creating a CloudWatch client using Boto3.
        
        Args:
            namespace (str): The namespace to associate with the CloudWatch metrics.
        """
        self.namespace = namespace
        try:
            self.cw_client = boto3.client("cloudwatch", region_name=app_config.AWS_REGION)
            logger.info(f"CloudWatch client initialized for region: {app_config.AWS_REGION}")
        except (ValueError, ClientError) as e:
            logger.error(f"Failed to initialize CloudWatch client: {e}")
            raise

    def put_metric(self, name: str, value: float, unit: str, dimensions: list = None) -> None:
        """
        Publishes a custom metric to AWS CloudWatch.
        
        Args:
            name (str): The name of the metric.
            value (float): The value of the metric.
            unit (str): The unit of the metric (e.g., 'Seconds', 'Bytes').
            dimensions (list, optional): A list of dimensions for the metric. Defaults to an empty list.
        
        Raises:
            Exception: If the metric publishing fails.
        """
        if dimensions is None:
            dimensions = []

        logger.info(f"Publishing metric {name}: {value} with unit {unit}")
        try:
            self.cw_client.put_metric_data(
                Namespace=self.namespace,
                MetricData=[{
                    "MetricName": name,
                    "Dimensions": dimensions,
                    "Value": value,
                    "Unit": unit
                }]
            )
            logger.info(f"Metric {name} was published successfully.")
        except ClientError as e:
            logger.error(f"Client error occurred while publishing metric {name}: {e}")
        except Exception as e:
            logger.error(f"Failed to publish metric {name}: {str(e)}")
