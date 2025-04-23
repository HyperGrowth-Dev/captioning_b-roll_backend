import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from fastapi import HTTPException
import logging
import time

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

class S3Service:
    def __init__(self):
        try:
            # Check for required environment variables
            required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION', 'S3_BUCKET_NAME']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION'),
                config=Config(signature_version='s3v4')
            )
            self.bucket_name = os.getenv('S3_BUCKET_NAME')
            
            # Verify bucket exists and is accessible
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Successfully initialized S3Service with bucket: {self.bucket_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize S3Service: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize S3 service: {str(e)}"
            )

    def generate_presigned_url(self, key: str, operation: str, expiration: int = 3600):
        """Generate a presigned URL for upload or download"""
        try:
            # For get operations, verify the file exists first
            if operation == 'get':
                try:
                    self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        raise HTTPException(status_code=404, detail="File not found in S3")
                    raise

            url = self.s3_client.generate_presigned_url(
                ClientMethod=f'{operation}_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            logger.info(f"Generated presigned URL for {operation} operation on key: {key}")
            return url
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def download_file(self, key: str, local_path: str):
        """Download a file from S3"""
        try:
            # First check if the file exists
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    raise HTTPException(status_code=404, detail="File not found in S3")
                raise

            logger.info(f"Downloading file from S3: {key} to {local_path}")
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(local_path) or '.', exist_ok=True)
            
            # Download the file
            self.s3_client.download_file(self.bucket_name, key, local_path)
            
            # Verify the file was downloaded and has content
            if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
                raise Exception("File download failed or file is empty")
                
            logger.info(f"File downloaded successfully: {key}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error downloading file from S3: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def upload_file(self, local_path: str, key: str):
        """Upload a file to S3"""
        try:
            # Check if the local file exists and is not empty
            if not os.path.exists(local_path):
                raise HTTPException(status_code=400, detail=f"Local file not found: {local_path}")
            if os.path.getsize(local_path) == 0:
                raise HTTPException(status_code=400, detail="File is empty")
                
            logger.info(f"Uploading file to S3: {local_path} to {key}")
            self.s3_client.upload_file(local_path, self.bucket_name, key)
            
            # Verify the upload was successful
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            except ClientError:
                raise HTTPException(status_code=500, detail="Upload verification failed")
                
            logger.info(f"File uploaded successfully: {key}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def file_exists(self, key: str, max_retries: int = 5, retry_delay: int = 2) -> bool:
        """Check if a file exists in S3 with retries for eventual consistency"""
        for attempt in range(max_retries):
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
                logger.info(f"File exists in S3: {key}")
                return True
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    if attempt < max_retries - 1:
                        logger.warning(f"File not found in S3 (attempt {attempt + 1}/{max_retries}): {key}")
                        logger.warning(f"Waiting {retry_delay} seconds before retrying...")
                        time.sleep(retry_delay)
                        continue
                    logger.info(f"File not found in S3 after {max_retries} attempts: {key}")
                    return False
                else:
                    logger.error(f"Error checking file existence in S3: {str(e)}")
                    return False
            except Exception as e:
                logger.error(f"Unexpected error checking file existence in S3: {str(e)}")
                return False
        return False 