import os
import logging
import json
import traceback
from remotion_lambda import RemotionClient, RenderMediaParams, Privacy, ValidStillImageFormats
from dotenv import load_dotenv
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

class RemotionService:
    def __init__(self):
        self.region = os.getenv('REMOTION_APP_REGION', 'us-east-2')
        self.function_name = 'remotion-render-4-0-273-mem2048mb-disk2048mb-120sec'
        self.serve_url = os.getenv('REMOTION_APP_SERVE_URL')
        
        if not all([self.region, self.function_name, self.serve_url]):
            raise ValueError("Missing required environment variables for Remotion Lambda")
        
        self.client = RemotionClient(
            region=self.region,
            serve_url=self.serve_url,
            function_name=self.function_name
        )

    def process_video(self, video_url: str, output_key: str, captions: list = None, broll_clips: list = None, video_width: int = None, video_height: int = None, fps: float = 30, font: str = 'Barlow-BlackItalic', color: str = 'white', font_size: int = 48, highlight_type: str = 'background', video_duration: float = None) -> dict:
        try:
            logger.info(f"RemotionService processing video with fps={fps}, duration={video_duration}")
            
            # Use provided dimensions
            main_width = video_width or 607  # Default to 607 if not provided
            main_height = video_height or 1080  # Default to 1080 if not provided
            logger.info(f"Using video dimensions: {main_width}x{main_height}")
            
            # Use provided video duration or calculate from captions
            if video_duration is None and captions and len(captions) > 0:
                video_duration = captions[-1]['endFrame'] / fps  # Convert frames to seconds using actual FPS
                logger.info(f"Using video duration from captions: {video_duration:.2f}s")
            elif video_duration is not None:
                logger.info(f"Using provided video duration: {video_duration:.2f}s")
            
            # Use captions directly if provided
            remotion_captions = captions or []

            # Use provided b-roll clips or empty list
            broll_clips = broll_clips or []
            logger.info(f"Using {len(broll_clips)} b-roll clips")

            # Set render request parameters
            input_props = {
                'videoSrc': video_url,
                'captions': remotion_captions,
                'font': font,
                'fontSize': font_size,
                'color': color,
                'position': 'bottom',
                'highlightType': highlight_type,
                'brollClips': broll_clips,
                'videoDuration': video_duration,
                'videoWidth': main_width,
                'videoHeight': main_height,
                'fps': fps,
                'compositionFps': fps
            }

            render_params = RenderMediaParams(
                composition="CaptionVideo",
                privacy=Privacy.PUBLIC,
                image_format=ValidStillImageFormats.JPEG,
                input_props=input_props,
                out_name=output_key
            )
            
            logger.info("Starting Remotion render")
            render_response = self.client.render_media_on_lambda(render_params)
            logger.info(f"Render response: {render_response}")
            
            if not render_response:
                raise Exception("Failed to start render")

            self.bucket_name = render_response.bucket_name
            logger.info(f"Render started successfully with bucket: {self.bucket_name}")

            return {
                'status': 'processing',
                'renderId': render_response.render_id,
                'bucketName': render_response.bucket_name
            }

        except Exception as e:
            logger.error(f"Error in RemotionService: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise

    def check_progress(self, render_id: str) -> Dict[str, Any]:
        """Check the progress of a video render"""
        try:
            # Get the render status from Remotion
            progress_response = self.client.get_render_progress(
                render_id=render_id,
                bucket_name=self.bucket_name
            )
            
            if progress_response.done:
                return {
                    'status': 'done',
                    'message': 'Video processing complete',
                    'url': progress_response.outputFile
                }
            elif progress_response.fatalErrorEncountered:
                return {
                    'status': 'failed',
                    'message': f'Video processing failed: {progress_response.errors}'
                }
            else:
                return {
                    'status': 'processing',
                    'message': 'Video is being processed',
                    'progress': progress_response.overallProgress
                }
        except Exception as e:
            logger.error(f"Error checking progress: {str(e)}")
            raise

    def cleanup(self):
        """Clean up temporary files"""
        pass 