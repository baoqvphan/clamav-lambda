# ClamAV Virus Scanning Service

This project provides an automated solution to scan files uploaded to an S3 bucket for viruses using ClamAV. It integrates with AWS services like S3, CloudWatch, and SQS. Once a file is uploaded to S3, the service will:

1. Download the ClamAV virus signature database from S3 (if not already present).
2. Download the file from S3.
3. Run ClamAV to scan the file for viruses.
4. Tag the S3 file with the scan result (Clean/Infected).
5. Publish scan performance metrics to CloudWatch.
6. Send a summary of the scan to an SQS queue for further processing or notifications.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup and Configuration](#setup-and-configuration)
- [Services Overview](#services-overview)
- [How It Works](#how-it-works)

---

## Prerequisites

Before using this service, ensure that the following prerequisites are met:

1. **AWS Account**: You need an AWS account with permissions to interact with the following AWS services:
   - S3: For uploading and downloading files.
   - CloudWatch: For publishing metrics.
   - SQS: For sending event summaries.
   
2. **ClamAV**: You will need access to the ClamAV virus scanner, which is used to scan the files for viruses.

3. **Docker** (Optional): If you want to test the Lambda function and ClamAV scanning locally.

---

## Setup and Configuration

1. **Clone the Repository**

Clone the repository to your local machine:

```bash
   git clone https://github.com/your-repository/clamav-scanner.git
   cd clamav-scanner
```

### 2. Install Dependencies

Install the required Python dependencies using pip:

```bash
pip install -r requirements.txt
```

### 3. AWS Configuration
Ensure that you have valid AWS credentials set up with access to S3 and CloudWatch. You can configure your AWS credentials using the AWS CLI:

```bash
aws configure
```

### 4. Configure the ClamAV Database
Make sure you have the ClamAV database available in your S3 bucket. The freshclam.conf file should also be in place for configuration.

### 5. Running the Lambda Function
You can deploy the Lambda function using the AWS Lambda Console or using AWS SAM/Serverless Framework.

If you're testing locally:

```bash
python lambda_function.py
```

### 6. Docker Build and Run
If you'd like to use Docker for running ClamAV scanning, use the provided Dockerfile. Build and run the Docker image as follows:

```bash
docker build -t clamav-scanner .
docker run -it clamav-scanner
```
This will build the ClamAV environment and scan files as described in the services.

## How It Works  
* S3 Event Trigger: When a new file is uploaded to S3, an event is sent to the Lambda function.
* Download File: The Lambda function uses S3Service to download the file to a local directory.
* Virus Scan: The ClamavService uses ClamAV to scan the file.
* CloudWatch Metrics: Performance metrics are sent to CloudWatch, including scan time and file size.
* Tagging Files: The file is tagged in S3 with the scan result (clamav-scan-status), either CLEAN or INFECTED.

## Example S3 Event
This Lambda function is triggered by S3 events such as an object upload:

```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "your-bucket-name"
        },
        "object": {
          "key": "path/to/your/file.txt"
        }
      }
    }
  ]
}
```
