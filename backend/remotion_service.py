import os
import json
import logging
from typing import List, Dict, Any
from .remotion_local_service import RemotionLocalService

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RemotionService:
    def __init__(self):
        logger.info("Initializing RemotionService")
        self.local_service = RemotionLocalService()
        logger.info("RemotionService initialized successfully")

    def process_video(
        self,
        video_url: str,
        captions: List[Dict[str, Any]],
        settings: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Process a video with captions using local Remotion rendering
        
        Args:
            video_url: URL to the input video (S3 URL)
            captions: List of caption objects with text and timing
            settings: Video processing settings (font, color, etc.)
            
        Returns:
            Dictionary containing the output path
        """
        try:
            logger.info(f"Starting video processing for: {video_url}")
            
            # Process video using local renderer
            result = self.local_service.process_video(video_url, captions, settings)
            
            logger.info("Video processing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise

    def cleanup(self, output_path: str):
        """Clean up temporary files"""
        self.local_service.cleanup(output_path) 