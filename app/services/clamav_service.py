import os
import subprocess
from time import time
from app.core.logging_config import LoggerHelper
from app.services.s3_service import S3Service
from app.services.cloud_watch_service import CloudWatchService
from app.services.sqs_service import SqsService
from urllib.parse import unquote_plus
import app.core.app_config as app_config
import app.core.constants as constants


logger = LoggerHelper.get_logger(__name__)
os.environ["LD_LIBRARY_PATH"] = app_config.CLAMAV_LIB_PATH

class ClamavService:
    """
    ClamAV service to scan files for viruses using ClamAV.
    It integrates with S3 to download files, scans them, and publishes scan results to CloudWatch.
    """
    def __init__(self):
        # Initialize S3 and CloudWatch clients
        self.s3_service = S3Service()
        self.cw_service = CloudWatchService("clamav-virus-scanner")
        self.sqs_service = SqsService()

    def process(self, s3_event_details: dict) -> None:
        """
        Processes an S3 event to download, scan, and report the results.
        
        Args:
            s3_event_details (dict): The event details from S3 that contain the bucket and object key.
        """
        source_bucket_name = s3_event_details["bucket"]["name"]
        s3_object_key = unquote_plus(s3_event_details["object"]["key"])
        
        summary = {}
        start_time = time()

        if not s3_object_key.endswith("/"):
            # Download ClamAV database if not already present
            self.download_clamav_signature_from_s3()

            if os.path.exists(app_config.CLAMAV_DB_PATH):
                # File will be temporarily stored in a tmp folder
                local_file_path = f"{app_config.TMP_PATH}/{s3_object_key.split('/')[-1]}"
                self.s3_service.download_s3_file(source_bucket_name, s3_object_key, local_file_path)

                # Run ClamAV scan
                summary = self.scan(source_bucket_name, s3_object_key, local_file_path)
            else:
                summary = {
                    "source": "clamav-scanner",
                    "bucket_name": source_bucket_name,
                    "object_key": s3_object_key,
                    "status": "error",
                    "message": "ClamAV database not found.",
                }
        else:
            summary = {
                "source": "clamav-scanner",
                "bucket_name": source_bucket_name,
                "object_key": s3_object_key,
                "status": "ignored",
                "message": "S3 event triggered for a non-file object",
            }

        scan_time = time() - start_time
        summary["scan_time"] = scan_time

        dimensions = [
            {"Name": "BucketName", "Value": source_bucket_name},
            {"Name": "FileName", "Value": s3_object_key}
        ]

        # Publish performance metrics to CloudWatch
        self.cw_service.put_metric("ScanTime", scan_time, "Seconds", dimensions)
        self.cw_service.put_metric("FileSize", summary.get("file_size", 0), "Megabytes", dimensions)

        # Publish the scanning results to SQS
        if app_config.SQS_QUEUE_URL:
            self.sqs_service.send_event(summary)

    def download_clamav_signature_from_s3(self) -> None:
        """
        Downloads the ClamAV database from the S3 bucket to the local machine.

        This is required before scanning files.
        """
        try:
            signature_path = os.path.join(app_config.CLAMAV_DB_PATH, 'clamav-db.tar.gz')
            self.s3_service.download_s3_file(
                app_config.CLAMAV_DB_S3_BUCKET_NAME,
                app_config.CLAMAV_DB_S3_KEY,
                signature_path
            )

            # Extract Clamav signatures
            import tarfile
            with tarfile.open(signature_path, 'r:gz') as tar:
                tar.extractall(path=app_config.CLAMAV_DB_PATH)
                logger.info(f"ClamAV signature extracted to {app_config.CLAMAV_DB_PATH}")
        except Exception as e:
            logger.error(f"Error downloading and extracting ClamAV database from S3: {e}")

    def scan(self, source_bucket: str, s3_object_key: str, local_file: str) -> dict:
        """
        Scans the file using ClamAV and updates the status in S3.
        
        Args:
            source_bucket (str): The S3 bucket where the file is stored.
            s3_object_key (str): The S3 object key (file path).
            local_file (str): The local path to the downloaded file.

        Returns:
            dict: A dictionary containing scan results (status, message).
        """
        logger.info(f"Started ClamAV scanning for {s3_object_key}...")

        try:
            clamscan_command = [
                f"{app_config.CLAMAV_LIB_PATH}/clamscan", "--database",
                app_config.CLAMAV_DB_PATH,
                local_file
            ]
            result = subprocess.run(clamscan_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode("utf-8")

            status = constants.CLEAN if "Infected files: 0" in output else constants.INFECTED
            logger.info(f"Scan completed for {s3_object_key}: {status}")

            # Tag scan result status to the S3 file
            self.s3_service.put_tags(source_bucket, s3_object_key, {"clamav-scan-status": status})

            # Return scan result summary
            return {
                "source": "clamav-scanner",
                "bucket_name": source_bucket,
                "object_key": s3_object_key,
                "status": status,
                "message": output,
            }

        except Exception as e:
            logger.error(f"Error scanning {s3_object_key}: {e}")
            return {
                "source": "clamav-scanner",
                "bucket_name": source_bucket,
                "object_key": s3_object_key,
                "status": "error",
                "message": str(e),
            }
