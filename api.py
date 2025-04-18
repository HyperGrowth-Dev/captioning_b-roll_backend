from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import os
from main import VideoProcessor
import tempfile
import shutil
from utils import setup_logging, ensure_directory
from datetime import datetime
import traceback
import time
from services.s3_service import S3Service
import uuid
import logging
from botocore.exceptions import ClientError
import asyncio
import boto3

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Video Caption and B-Roll API",
    description="API for processing videos to add captions and generate b-roll suggestions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create necessary directories
ensure_directory('uploads')
ensure_directory('output')

# Initialize video processor
try:
    video_processor = VideoProcessor()
    logger.info("VideoProcessor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize VideoProcessor: {str(e)}")
    raise

s3_service = S3Service()

@app.get("/api/")
async def root():
    """Root endpoint that returns API information"""
    return {
        "name": "Video Caption and B-Roll API",
        "version": "1.0.0",
        "endpoints": {
            "/": "This information",
            "/health": "Check API health status",
            "/docs": "API documentation (Swagger UI)",
            "/redoc": "API documentation (ReDoc)",
            "/api/process-video": "Upload and process a video",
            "/api/download/{filename}": "Download a processed video"
        }
    }

@app.post("/api/process-video")
async def process_video(
    file: UploadFile = File(...),
    font: str = Form("Montserrat-Bold"),  # Default font
    color: str = Form("white"),  # Default color
    font_size: int = Form(48)  # Default font size
):
    """Process uploaded video file"""
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process video
        processor = VideoProcessor()
        output_path = processor.process_video(
            file_path,
            font=font,
            color=color,
            font_size=font_size
        )
        
        # Clean up uploaded file
        os.remove(file_path)
        
        # Return the filename of the processed video
        return JSONResponse(
            content={
                "message": "Video processed successfully",
                "filename": os.path.basename(output_path),
                "download_url": f"/api/download/{os.path.basename(output_path)}"
            }
        )
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_video(filename: str):
    """Download a processed video file"""
    file_path = os.path.join('output', filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if the file is a video
    if not filename.lower().endswith(('.mp4', '.avi', '.mov')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only video files are allowed.")
    
    # Get the content type based on file extension
    content_type = {
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime'
    }.get(os.path.splitext(filename)[1].lower(), 'application/octet-stream')
    
    return FileResponse(
        file_path,
        filename=filename,
        media_type=content_type,
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )

@app.get("/api/health")
async def health_check():
    """Check if the API is healthy and all services are available"""
    try:
        # Check if required environment variables are set
        required_vars = ['OPENAI_API_KEY', 'PEXELS_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "missing_environment_variables": missing_vars
                }
            )
        
        return JSONResponse(content={"status": "healthy"})
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/api/get-upload-url")
async def get_upload_url():
    """Generate a pre-signed URL for uploading a video to S3"""
    try:
        logger.info("Generating upload URL")
        
        # Generate a unique key for the upload
        upload_key = f"uploads/{uuid.uuid4()}.mp4"
        logger.info(f"Generated upload key: {upload_key}")
        
        # Generate pre-signed URL
        upload_url = s3_service.generate_presigned_url(upload_key, "put")
        logger.info("Successfully generated upload URL")
        
        return {
            "upload_url": upload_url,
            "key": upload_key
        }
    except Exception as e:
        logger.error(f"Error generating upload URL: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate upload URL: {str(e)}"
        )

@app.post("/api/process")
async def process_video_s3(
    input_key: str = Form(...),
    font: str = Form(...),
    color: str = Form(...),
    font_size: int = Form(24)
):
    """Process a video from S3 with the given options"""
    logger.info(f"Processing video request received with options: input_key={input_key}, font={font}, color={color}, font_size={font_size}")
    
    try:
        # Generate a unique output key
        process_id = str(uuid.uuid4())
        output_key = f"processed/{process_id}.mp4"
        logger.info(f"Generated output key: {output_key}")
        
        # Download the video from S3
        local_input_path = f"/tmp/{uuid.uuid4()}.mp4"
        logger.info(f"Downloading video from S3 to {local_input_path}")
        await s3_service.download_file(input_key, local_input_path)
        
        # Process the video
        logger.info(f"Processing video with options: font={font}, color={color}, font_size={font_size}")
        
        # Create VideoProcessor instance and process the video
        processor = VideoProcessor()
        output_path = processor.process_video(
            local_input_path,
            font=font,
            color=color,
            font_size=font_size
        )
        
        # Upload the processed video to S3
        logger.info(f"Uploading processed video to S3 with key: {output_key}")
        await s3_service.upload_file(output_path, output_key)
        
        # Verify the file exists
        if not s3_service.file_exists(output_key):
            logger.error(f"Failed to verify uploaded file in S3: {output_key}")
            raise HTTPException(status_code=500, detail="Failed to verify uploaded file in S3")
        logger.info(f"Successfully verified file in S3: {output_key}")
        
        # Clean up local files
        logger.info("Cleaning up temporary files")
        os.remove(local_input_path)
        os.remove(output_path)
        
        logger.info("Video processing completed successfully")
        return {
            "status": "success",
            "output_key": output_key
        }
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get-download-url/{key:path}")
async def get_download_url(key: str):
    """Get a pre-signed URL for downloading a processed video"""
    logger.info(f"Received download URL request for key: {key}")
    try:
        # List contents of the directory to help debug
        directory = '/'.join(key.split('/')[:-1])
        logger.info(f"Listing contents of directory: {directory}")
        try:
            response = s3_service.s3_client.list_objects_v2(
                Bucket=s3_service.bucket_name,
                Prefix=directory
            )
            if 'Contents' in response:
                logger.info(f"Found files: {[obj['Key'] for obj in response['Contents']]}")
            else:
                logger.warning(f"No files found in directory: {directory}")
        except Exception as e:
            logger.error(f"Error listing directory contents: {str(e)}")

        # Try to get the download URL
        try:
            url = s3_service.generate_presigned_url(key, 'get')
            logger.info(f"Successfully generated download URL for key: {key}")
            return {"download_url": url}
        except HTTPException as e:
            if e.status_code == 404:
                logger.error(f"File not found in S3: {key}")
                raise HTTPException(
                    status_code=404,
                    detail=f"File not found in S3. Please check if the file exists at: {key}"
                )
            raise
    except Exception as e:
        logger.error(f"Error getting download URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-s3-permissions")
async def test_s3_permissions():
    """Test S3 permissions"""
    try:
        results = {
            "bucket_exists": False,
            "can_list": False,
            "can_get": False,
            "can_put": False,
            "errors": []
        }
        
        # Test if bucket exists
        try:
            s3_service.s3_client.head_bucket(Bucket=s3_service.bucket_name)
            results["bucket_exists"] = True
        except Exception as e:
            results["errors"].append(f"Bucket check error: {str(e)}")
        
        # Test list operation
        try:
            s3_service.s3_client.list_objects_v2(
                Bucket=s3_service.bucket_name,
                MaxKeys=1
            )
            results["can_list"] = True
        except Exception as e:
            results["errors"].append(f"List error: {str(e)}")
        
        # Test put operation
        test_key = "test-permissions/test.txt"
        try:
            s3_service.s3_client.put_object(
                Bucket=s3_service.bucket_name,
                Key=test_key,
                Body="test"
            )
            results["can_put"] = True
            
            # Test get operation
            try:
                s3_service.s3_client.get_object(
                    Bucket=s3_service.bucket_name,
                    Key=test_key
                )
                results["can_get"] = True
            except Exception as e:
                results["errors"].append(f"Get error: {str(e)}")
                
            # Clean up
            s3_service.s3_client.delete_object(
                Bucket=s3_service.bucket_name,
                Key=test_key
            )
        except Exception as e:
            results["errors"].append(f"Put error: {str(e)}")
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/check-file/{key}")
async def check_file(key: str):
    """Check if a file exists in S3"""
    try:
        logger.info(f"Checking if file exists: {key}")
        exists = s3_service.file_exists(key)
        logger.info(f"File exists check result: {exists}")
        return {"exists": exists}
    except Exception as e:
        logger.error(f"Error checking file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API server on http://localhost:8000")
    uvicorn.run(
        "api:app",
        host="0.0.0.0",  # Allow external connections
        port=8000,
        reload=True,     # Enable auto-reload for development
        log_level="info"
    ) 