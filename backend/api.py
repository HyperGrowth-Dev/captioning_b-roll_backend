from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
import logging
from backend.services.remotion_service import RemotionService
from backend.services.s3_service import S3Service
from utils import FFmpegUtils
import os
import uuid
from pydantic import BaseModel
import traceback
from caption_processor import CaptionProcessor

# Initialize logger
logger = logging.getLogger(__name__)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
        logging.FileHandler('app.log')  # File handler
    ]
)

# Set specific loggers to appropriate levels
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize services
remotion_service = RemotionService()
s3_service = S3Service()

class Caption(BaseModel):
    text: str
    start: float
    end: float

class VideoSettings(BaseModel):
    captions: List[Caption]
    font: str = "Barlow"
    fontSize: int = 48
    color: str = "white"
    position: str = "bottom"
    highlightType: str = "background"

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
            "/api/process": "Process a video",
            "/api/upload": "Upload a video",
            "/api/get-upload-url": "Get presigned URL for upload",
            "/api/get-download-url/{key}": "Get presigned URL for download"
        }
    }

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
        try:
            upload_url = s3_service.generate_presigned_url(upload_key, "put")
            logger.info("Successfully generated upload URL")
            
            return {
                "upload_url": upload_url,
                "key": upload_key
            }
        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate upload URL: {str(e)}"
            )
            
    except Exception as e:
        logger.error(f"Error in get_upload_url endpoint: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate upload URL: {str(e)}"
        )

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
        return {"exists": False}

@app.post("/api/process")
async def process_video(
    input_key: str = Form(...),
    font: str = Form(...),
    color: str = Form(...),
    font_size: int = Form(32),
    highlight_type: str = Form("background"),
    broll_enabled: bool = Form(True),
    video_width: int = Form(607),
    video_height: int = Form(1080)
):
    try:
        # Get the S3 URL for the input video
        try:
            video_url = s3_service.get_download_url(input_key)
            logger.info(f"Retrieved S3 URL for video: {video_url}")
        except Exception as e:
            logger.error(f"Error getting S3 URL: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get video URL: {str(e)}"
            )
        # Download video to temp directory
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        video_path = os.path.join(temp_dir, f"{input_key}.mp4")
        await s3_service.download_file(input_key, video_path)

        # Get video info including FPS
        width, height, duration, fps = FFmpegUtils.get_video_info(video_path)
        logger.info(f"Video FPS: {fps}, Duration: {duration}")

        # Extract audio
        audio_path = os.path.join(temp_dir, f"{input_key}.wav")
        FFmpegUtils.extract_audio(video_path, audio_path)

        # Generate captions
        caption_processor = CaptionProcessor(fps=fps)  # Pass the actual FPS
        segments = caption_processor.generate_captions(audio_path)
        
        if not segments:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate captions"
            )

        # Create caption clips
        caption_clips = caption_processor.create_caption_clips(
            segments,
            video_width=video_width,
            video_height=video_height,
            font=font,
            color=color,
            font_size=font_size
        )

        # Process video using Remotion
        output_key = f"processed/{os.path.basename(input_key)}"
        result = remotion_service.process_video(
            video_url, 
            output_key, 
            caption_clips, 
            broll_enabled=broll_enabled,
            video_width=video_width,
            video_height=video_height,
            fps=fps,  # Pass the FPS to Remotion service
            font=font,
            color=color,
            font_size=font_size,
            highlight_type=highlight_type,
            video_duration=duration  # Pass the actual video duration
        )
        
        # Clean up temporary files
        os.remove(video_path)
        os.remove(audio_path)
        
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/check_progress/{render_id}")
async def check_progress(render_id: str):
    try:
        result = remotion_service.check_progress(render_id)
        return result
    except Exception as e:
        logger.error(f"Error checking progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Upload to S3
        s3_url = await s3_service.upload_file(file, unique_filename)
        
        return {"url": s3_url}
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 