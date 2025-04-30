from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import traceback
from typing import Dict, Any
from remotion_local_service import RemotionLocalService
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
remotion_service = RemotionLocalService()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/process-video")
async def process_video(
    video_url: str,
    font: str = "Montserrat-Bold",
    font_size: int = 48,
    color: str = "white",
    position: str = "bottom",
    highlight_type: str = "background",
    enable_broll: bool = True,
    width: int = 1920,
    height: int = 1080
):
    try:
        settings = {
            "font": font,
            "font_size": font_size,
            "color": color,
            "position": position,
            "highlight_type": highlight_type,
            "enable_broll": enable_broll,
            "width": width,
            "height": height
        }
        
        logger.info(f"Processing video with settings: {settings}")
        
        # Process the video
        result = await remotion_service.process_video(video_url, settings)
        
        return {
            "status": "success",
            "message": "Video processed successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 