from fastapi import FastAPI, UploadFile, File, HTTPException
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

# Initialize logger
logger = setup_logging('api', 'api.log')

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

@app.get("/")
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
            "/process-video": "Upload and process a video",
            "/download/{filename}": "Download a processed video"
        }
    }

@app.post("/process-video")
async def process_video(file: UploadFile = File(...)):
    """
    Process a video file to:
    1. Generate captions
    2. Analyze for b-roll opportunities
    3. Return both captions and b-roll suggestions
    """
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = os.path.splitext(file.filename)[0]
        # Always use .mp4 extension for processed videos
        processed_filename = f"processed_{original_filename}_{timestamp}.mp4"
        
        # Save uploaded file to uploads directory
        upload_path = os.path.join('uploads', f"{original_filename}_{timestamp}{os.path.splitext(file.filename)[1]}")
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Saved uploaded file to: {upload_path}")
        
        # Process the video
        video_processor.process_video(upload_path)
        
        # Read the results
        output_dir = 'output'
        results = {
            'captions': [],
            'broll_suggestions': [],
            'processed_video': None
        }
        
        # Read captions if they exist
        captions_file = os.path.join(output_dir, 'captions.txt')
        if os.path.exists(captions_file):
            with open(captions_file, 'r') as f:
                results['captions'] = f.readlines()
        
        # Read b-roll analysis if it exists
        analysis_file = os.path.join(output_dir, 'broll_analysis.json')
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                results['broll_suggestions'] = f.read()
        
        # Get the processed video path
        processed_video = os.path.join(output_dir, 'processed_video.mp4')
        if os.path.exists(processed_video):
            # Add a small delay to ensure the file is fully written
            time.sleep(1)
            
            # Move the processed video to its final location
            processed_path = os.path.join(output_dir, processed_filename)
            logger.info(f"Moving processed video from {processed_video} to {processed_path}")
            
            # Try to move the file, if it fails, try to copy and then delete
            try:
                shutil.move(processed_video, processed_path)
            except Exception as e:
                logger.warning(f"Failed to move file, trying copy and delete: {str(e)}")
                shutil.copy2(processed_video, processed_path)
                os.remove(processed_video)
            
            results['processed_video'] = processed_filename
            logger.info(f"Successfully moved processed video to {processed_path}")
        else:
            logger.error(f"Processed video not found at {processed_video}")
            raise HTTPException(status_code=500, detail="Processed video not found")
        
        return JSONResponse(content=results)
            
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
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

@app.get("/health")
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