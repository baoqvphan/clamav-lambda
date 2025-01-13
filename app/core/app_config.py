import os
from dotenv import load_dotenv
from app.core.logging_config import LoggerHelper
from app.util.get_ssm_parameter_util import get_ssm_parameter


# Setup logging before any other operations
logger = LoggerHelper.get_logger(__name__)

# Environment variables
ENV = os.environ.get('ENV', 'local')
SERVICE_NAME = os.environ.get('SERVICE')
AWS_REGION = os.environ.get('AWS_REGION')

TMP_PATH = os.getenv("TMP_PATH", "/tmp")
CLAMAV_LIB_PATH = os.getenv("CLAMAV_LIB_PATH", "/opt/clamav")
CLAMAV_DB_PATH = f"{TMP_PATH}/clamav-db" # where ClamAV definitions are stored

# Load configuration based on environment
if ENV != 'local':
    CLAMAV_DB_S3_BUCKET_NAME = get_ssm_parameter(f"/{ENV}/{SERVICE_NAME}/CLAMAV_DB_S3_BUCKET_NAME", AWS_REGION)
    CLAMAV_DB_S3_KEY = get_ssm_parameter(f"/{ENV}/{SERVICE_NAME}/CLAMAV_DB_S3_KEY", AWS_REGION)
    
    # SQS URL and configurations
    SQS_QUEUE_URL = get_ssm_parameter(f"/{ENV}/{SERVICE_NAME}/SQS_QUEUE_URL", AWS_REGION)
else:
    load_dotenv()
    CLAMAV_DB_S3_BUCKET_NAME = os.getenv("BUCKET_NAME", "")
    CLAMAV_DB_S3_KEY = os.getenv("CLAMAV_DB_S3_KEY", "clamav/signatures/clamav-db.tar.gz")

    # SQS URL and configurations
    SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "")

if not all([CLAMAV_DB_S3_BUCKET_NAME, CLAMAV_DB_S3_KEY]):
    logger.error("Clamav database bucket and folder name are not set.")

