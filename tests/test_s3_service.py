import pytest
import os
import tempfile
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from services.s3_service import S3Service
from fastapi import HTTPException
import boto3
from moto import mock_s3
import uuid

# Test data
TEST_BUCKET_NAME = "test-bucket"
TEST_FILE_CONTENT = b"Test file content"
TEST_KEY = "test-file.txt"

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_REGION'] = 'us-east-1'
    os.environ['S3_BUCKET_NAME'] = TEST_BUCKET_NAME

@pytest.fixture
def s3(aws_credentials):
    """S3 mock fixture."""
    with mock_s3():
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=TEST_BUCKET_NAME)
        yield s3

@pytest.fixture
def s3_service(s3):
    """S3Service fixture."""
    return S3Service()

@pytest.fixture
def test_file():
    """Create a temporary test file."""
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        f.write(TEST_FILE_CONTENT)
        f.flush()
        yield f.name
    os.unlink(f.name)

def test_generate_presigned_url(s3_service, s3):
    """Test generating presigned URLs."""
    # Test upload URL
    upload_url = s3_service.generate_presigned_url(TEST_KEY, "put")
    assert upload_url is not None
    assert "https://" in upload_url
    assert TEST_KEY in upload_url

    # Test download URL
    download_url = s3_service.generate_presigned_url(TEST_KEY, "get")
    assert download_url is not None
    assert "https://" in download_url
    assert TEST_KEY in download_url

    # Test with custom expiration
    custom_url = s3_service.generate_presigned_url(TEST_KEY, "get", expiration=7200)
    assert custom_url is not None

@pytest.mark.asyncio
async def test_upload_file(s3_service, s3, test_file):
    """Test file upload."""
    test_key = f"test-{uuid.uuid4()}.txt"
    
    # Verify file exists and has content
    assert os.path.exists(test_file)
    assert os.path.getsize(test_file) > 0
    
    await s3_service.upload_file(test_file, test_key)
    
    # Verify file exists in S3
    response = s3.head_object(Bucket=TEST_BUCKET_NAME, Key=test_key)
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200

@pytest.mark.asyncio
async def test_download_file(s3_service, s3, test_file):
    """Test file download."""
    # First upload a file
    test_key = f"test-{uuid.uuid4()}.txt"
    
    # Upload using the S3 client directly
    with open(test_file, 'rb') as f:
        s3.put_object(Bucket=TEST_BUCKET_NAME, Key=test_key, Body=f.read())
    
    # Create a temporary directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        download_path = os.path.join(temp_dir, "downloaded.txt")
        
        # Download the file
        await s3_service.download_file(test_key, download_path)
        
        # Verify content
        assert os.path.exists(download_path)
        assert os.path.getsize(download_path) > 0
        with open(download_path, 'rb') as f:
            content = f.read()
            assert content == TEST_FILE_CONTENT

def test_file_exists(s3_service, s3, test_file):
    """Test file existence check."""
    # Upload a test file
    test_key = f"test-{uuid.uuid4()}.txt"
    with open(test_file, 'rb') as f:
        s3.put_object(Bucket=TEST_BUCKET_NAME, Key=test_key, Body=f.read())
    
    # Test existing file
    assert s3_service.file_exists(test_key) is True
    
    # Test non-existent file
    assert s3_service.file_exists("non-existent-file.txt") is False

@pytest.mark.asyncio
async def test_error_handling(s3_service):
    """Test error handling."""
    # Test non-existent file download
    with pytest.raises(HTTPException) as exc_info:
        await s3_service.download_file("non-existent-file.txt", "dummy.txt")
    assert exc_info.value.status_code == 404
    assert "File not found in S3" in str(exc_info.value.detail)
    
    # Test invalid upload (non-existent file)
    with pytest.raises(HTTPException) as exc_info:
        await s3_service.upload_file("non-existent-file.txt", "dummy.txt")
    assert exc_info.value.status_code == 400
    assert "Local file not found" in str(exc_info.value.detail)
    
    # Test empty file upload
    with tempfile.NamedTemporaryFile(delete=False) as empty_file:
        empty_file_path = empty_file.name
    try:
        with pytest.raises(HTTPException) as exc_info:
            await s3_service.upload_file(empty_file_path, "empty.txt")
        assert exc_info.value.status_code == 400
        assert "File is empty" in str(exc_info.value.detail)
    finally:
        os.unlink(empty_file_path)

def test_retry_logic(s3_service, s3):
    """Test retry logic for file existence check."""
    # Test with non-existent file and custom retry parameters
    assert s3_service.file_exists("non-existent-file.txt", max_retries=2, retry_delay=1) is False 