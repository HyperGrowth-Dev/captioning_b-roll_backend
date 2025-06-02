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

# Get logger
logger = logging.getLogger(__name__)

class RemotionLocalService:
    def __init__(self):
        logger.info("Initializing RemotionLocalService")
        self.temp_dir = tempfile.mkdtemp()
        self.remotion_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "remotion")
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        self.s3_service = S3Service()
        self.caption_processor = CaptionProcessor()
        self.bundle_path = os.path.join(self.remotion_dir, "bundle")
        self.bundle_exists = os.path.exists(self.bundle_path)
        logger.info(f"Remotion bundle exists: {self.bundle_exists}")
        
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
            
            # Download video to the Remotion public directory
            video_filename = f"input_{key.replace('/', '_')}.mp4"
            video_path = os.path.join(self.remotion_dir, "public", video_filename)
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            
            logger.info(f"Downloading video to {video_path}")
            await self.s3_service.download_file(key, video_path)
            
            # Use the local URL for Remotion
            local_video_url = f"/public/{video_filename}"
            
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
                "videoSrc": local_video_url,
                "captions": caption_clips,
                "font": settings.get("font", "Montserrat-Bold"),
                "fontSize": settings.get("font_size", 48),
                "color": settings.get("color", "white"),
                "position": "bottom",
                "highlightType": settings.get("highlight_type", "background")
            }

            logger.info(f"Highlight type from settings: {settings.get('highlight_type')}")
            logger.info(f"Final input_props: {input_props}")

            # Save input properties to a temporary file
            input_props_path = os.path.join(self.temp_dir, "input.json")
            with open(input_props_path, "w") as f:
                json.dump(input_props, f)
            logger.info(f"Saved input properties to {input_props_path}")

            # Set output path
            output_path = os.path.join(self.temp_dir, "output.mp4")
            logger.info(f"Output will be saved to {output_path}")

            # Only build the project if the bundle doesn't exist
            if not self.bundle_exists:
                logger.info("Building Remotion project...")
                build_cmd = [
                    "npx", "remotion", "bundle", 
                    os.path.join(self.remotion_dir, "src", "compositions", "Root.tsx")
                ]
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

                self.bundle_exists = True
                logger.info("Remotion project built successfully")
            else:
                logger.info("Using existing Remotion bundle")

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
                "--timeout", "300000",
                "--log", "info"
            ]

            logger.info(f"Starting Remotion render with command: {' '.join(render_cmd)}")
            
            # Create a process with real-time output
            process = subprocess.Popen(
                render_cmd,
                cwd=self.remotion_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Clean and log the output
                    cleaned_output = output.strip()
                    if cleaned_output:
                        logger.info(f"Remotion: {cleaned_output}")
                        print(f"Remotion: {cleaned_output}")  # Print to terminal

            # Get the return code
            return_code = process.poll()
            if return_code != 0:
                error_msg = f"Remotion render failed with return code {return_code}"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info("Remotion render completed successfully")

            # Copy the processed video to the output directory
            final_output_path = os.path.join(self.output_dir, f"processed_{os.path.basename(output_path)}")
            shutil.copy2(output_path, final_output_path)
            logger.info(f"Copied processed video to {final_output_path}")

            # Clean up the video file after rendering
            try:
                os.remove(video_path)
                logger.info(f"Cleaned up temporary video file: {video_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up video file: {str(e)}")

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