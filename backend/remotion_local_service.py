import os
import json
import logging
import subprocess
import tempfile
import shutil
from typing import List, Dict, Any
from pathlib import Path
from services.s3_service import S3Service

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RemotionLocalService:
    def __init__(self):
        logger.info("Initializing RemotionLocalService")
        self.temp_dir = tempfile.gettempdir()
        self.remotion_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'remotion')
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        self.s3_service = S3Service()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Validate Remotion directory exists
        if not os.path.exists(self.remotion_dir):
            raise ValueError(f"Remotion directory not found at: {self.remotion_dir}")
        
        logger.info("RemotionLocalService initialized successfully")

    def process_video(
        self,
        video_url: str,  # Changed from video_path to video_url
        caption_clips: List[Dict[str, Any]],
        settings: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Process a video with captions using local Remotion rendering
        
        Args:
            video_url: URL to the input video (S3 URL)
            caption_clips: List of caption clips from CaptionProcessor
            settings: Optional override settings for font, color, etc.
            
        Returns:
            Dictionary containing the output path
        """
        try:
            logger.info(f"Starting local video processing for: {video_url}")
            
            # Check if the URL is already a presigned URL
            if '?' in video_url and 'X-Amz-Signature' in video_url:
                presigned_url = video_url
                logger.info("Using provided presigned URL")
            else:
                # Extract the key from the URL if it's a full S3 URL
                if video_url.startswith('https://'):
                    # Extract the key from the URL
                    key = video_url.split(f'https://{self.s3_service.bucket_name}.s3.amazonaws.com/')[-1]
                    key = key.split('?')[0]  # Remove any query parameters
                else:
                    key = video_url
                
                # Get presigned URL for the video
                presigned_url = self.s3_service.get_download_url(key)
                logger.info(f"Got presigned URL for video: {presigned_url}")
            
            # Create a temporary directory for this render
            with tempfile.TemporaryDirectory() as temp_dir:
                # Prepare input props
                input_props = {
                    "videoSrc": presigned_url,  # Use the presigned URL
                    "captions": [
                        {
                            "text": clip["text"],
                            "startFrame": clip["startFrame"],
                            "endFrame": clip["endFrame"],
                            "words": [
                                {
                                    "text": word["text"],
                                    "startFrame": int(word["start"] * settings.get("fps", 30)),
                                    "endFrame": int(word["end"] * settings.get("fps", 30))
                                }
                                for word in clip.get("words", [])
                            ]
                        }
                        for clip in caption_clips
                    ],
                    "font": settings.get('font', 'Arial') if settings else 'Arial',
                    "fontSize": settings.get('fontSize', 48) if settings else 48,
                    "color": settings.get('color', '#ffffff') if settings else '#ffffff',
                    "position": settings.get('position', 0.8) if settings else 0.8,
                    "transitions": settings.get('transitions', {
                        "type": 'fade',
                        "duration": 15
                    }) if settings else {"type": 'fade', "duration": 15},
                    "highlightColor": settings.get('highlightColor', '#FFD700') if settings else '#FFD700'
                }
                
                # Write input props to a temporary file
                input_props_path = os.path.join(temp_dir, 'input_props.json')
                with open(input_props_path, 'w') as f:
                    json.dump(input_props, f)
                
                # Prepare output paths
                temp_output_path = os.path.join(temp_dir, 'output.mp4')
                
                # Extract just the UUID from the video URL for the final output filename
                if '?' in video_url:
                    # If it's a presigned URL, get the part before the query parameters
                    base_name = video_url.split('?')[0]
                else:
                    base_name = video_url
                
                # Extract just the UUID part
                uuid_part = base_name.split('/')[-1].split('.')[0]
                final_output_path = os.path.join(self.output_dir, f'processed_{uuid_part}.mp4')
                
                # Run Remotion render command with optimized settings
                cmd = [
                    'npx', 'remotion', 'render',
                    'src/compositions/Root.tsx',
                    'CaptionVideo',
                    temp_output_path,
                    '--props', input_props_path,
                    '--concurrency', '1',  # Reduce concurrency to prevent glitches
                    '--jpeg-quality', '100',  # Maximum quality (renamed from --quality)
                    '--codec', 'h264',     # Use h264 codec
                    '--crf', '18',         # High quality CRF value
                    '--pixel-format', 'yuv420p',  # Standard pixel format
                    '--audio-bitrate', '320k',    # High quality audio
                    '--frames-per-second', '30'   # Match input FPS
                ]
                
                logger.info(f"Running Remotion render command: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    cwd=self.remotion_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"Remotion render failed: {result.stderr}")
                    raise RuntimeError(f"Remotion render failed: {result.stderr}")
                
                logger.info("Remotion render completed successfully")
                
                # Copy the processed video to the output directory
                shutil.copy2(temp_output_path, final_output_path)
                logger.info(f"Saved processed video to: {final_output_path}")
                
                # Return the final output path
                return {
                    "output_path": final_output_path
                }
                
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise

    def cleanup(self, output_path: str):
        """Clean up temporary files"""
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            logger.error(f"Error cleaning up files: {str(e)}") 