import os
import json
import logging
import subprocess
import tempfile
import shutil
import traceback
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from services.s3_service import S3Service
from caption_processor import CaptionProcessor

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
        self.caption_processor = CaptionProcessor()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize temp_dir_manager
        self.temp_dir_manager = tempfile.TemporaryDirectory()
        
        # Validate Remotion directory exists
        if not os.path.exists(self.remotion_dir):
            raise ValueError(f"Remotion directory not found at: {self.remotion_dir}")
        
        logger.info("RemotionLocalService initialized successfully")

    async def process_video(self, video_url: str, settings: Dict[str, Any]) -> Dict[str, str]:
        """Process a video with captions using Remotion"""
        try:
            logger.info(f"Using temporary directory for rendering: {self.temp_dir}")
            
            # Extract the key from the video URL and ensure it has the uploads/ prefix
            key = video_url.split('/')[-1].split('?')[0]
            if not key.startswith('uploads/'):
                key = f"uploads/{key}"
            logger.info(f"Using S3 key: {key}")
            
            # Download video
            video_path = os.path.join(self.temp_dir, "input.mp4")
            logger.info(f"Downloading video to {video_path}")
            await self.s3_service.download_file(key, video_path)
            
            # Generate captions
            logger.info("Generating captions...")
            segments = self.caption_processor.generate_captions(video_path)
            
            # Create caption clips
            logger.info("Creating caption clips...")
            caption_clips = self.caption_processor.create_caption_clips(
                segments,
                settings.get("width", 1920),
                settings.get("height", 1080),
                font=settings.get("font", "Montserrat-Bold"),
                color=settings.get("color", "white"),
                font_size=settings.get("font_size", 48)
            )

            # Prepare input properties for Remotion
            input_props = {
                "videoSrc": video_url,
                "captions": caption_clips,
                "font": settings.get("font", "Montserrat-Bold"),
                "fontSize": settings.get("font_size", 48),
                "color": settings.get("color", "white"),
                "position": "bottom",
                "effect": True
            }

            # Save input properties to a temporary file
            input_props_path = os.path.join(self.temp_dir, "input.json")
            with open(input_props_path, "w") as f:
                json.dump(input_props, f)
            logger.info(f"Saved input properties to {input_props_path}")

            # Set output path
            output_path = os.path.join(self.temp_dir, "output.mp4")
            logger.info(f"Output will be saved to {output_path}")

            # Run Remotion render command
            # First build the project
            build_cmd = [
                "npx", "remotion", "bundle", 
                os.path.join(self.remotion_dir, "src", "compositions", "Root.tsx")
            ]
            logger.info(f"Building Remotion project with command: {' '.join(build_cmd)}")
            build_result = subprocess.run(
                build_cmd,
                cwd=self.remotion_dir,
                capture_output=True,
                text=True
            )

            if build_result.returncode != 0:
                error_msg = f"Remotion build failed: {build_result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info("Remotion project built successfully")

            # Now run the render command
            render_cmd = [
                "npx", "remotion", "render",
                os.path.join(self.remotion_dir, "src", "compositions", "Root.tsx"),
                "CaptionVideo",
                output_path,
                "--props", input_props_path,
                "--concurrency", "8",
                "--jpeg-quality", "70",
                "--codec", "h264",
                "--crf", "28",
                "--pixel-format", "yuv420p",
                "--audio-bitrate", "128k",
                "--frames-per-second", "24",
                "--timeout", "300000"
            ]

            logger.info(f"Starting Remotion render with command: {' '.join(render_cmd)}")
            result = subprocess.run(
                render_cmd,
                cwd=self.remotion_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                error_msg = f"Remotion render failed: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info("Remotion render completed successfully")

            # Copy the processed video to the output directory
            final_output_path = os.path.join(self.output_dir, f"processed_{os.path.basename(output_path)}")
            shutil.copy2(output_path, final_output_path)
            logger.info(f"Copied processed video to {final_output_path}")

            return {"output_path": final_output_path}

        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise

    def cleanup(self):
        """Clean up temporary files and directories"""
        try:
            if hasattr(self, 'temp_dir_manager'):
                self.temp_dir_manager.cleanup()
                logger.info("Cleaned up temporary directory")
        except Exception as e:
            logger.error(f"Error cleaning up: {str(e)}") 