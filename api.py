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
                "download_url": f"/download/{os.path.basename(output_path)}"
            }
        )
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
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