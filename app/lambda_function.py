from app.services.clamav_service import ClamavService


def lambda_handler(event, context):
    clamav_service = ClamavService()
    clamav_service.process(event["Records"][0]["s3"])
