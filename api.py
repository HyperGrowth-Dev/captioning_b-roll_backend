from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import os
from main import VideoProcessor
import tempfile
import shutil
from utils import setup_logging

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
            "/process-video": "Upload and process a video"
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
        # Create a temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file
            input_path = os.path.join(temp_dir, file.filename)
            with open(input_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"Processing video: {file.filename}")
            
            # Process the video
            video_processor.process_video(input_path)
            
            # Read the results
            output_dir = 'output'
            results = {
                'captions': [],
                'broll_suggestions': []
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
            
            return JSONResponse(content=results)
            
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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