import os
import logging
from remotion_lambda import RemotionClient, RenderMediaParams, Privacy, ValidStillImageFormats
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

logger = logging.getLogger(__name__)

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

    def process_video(self, video_url: str, output_key: str, captions: list = None) -> dict:
        try:
            # Set render request parameters
            render_params = RenderMediaParams(
                composition="CaptionVideo",
                privacy=Privacy.PUBLIC,
                image_format=ValidStillImageFormats.JPEG,
                input_props={
                    'videoSrc': video_url,
                    'hi': 'there'
                },
                out_name=output_key
            )

            # Start the render
            render_response = self.client.render_media_on_lambda(render_params)
            
            if not render_response:
                raise Exception("Failed to start render")

            # Poll for progress
            progress_response = self.client.get_render_progress(
                render_id=render_response.render_id,
                bucket_name=render_response.bucket_name
            )

            while progress_response and not progress_response.done:
                logger.info(f"Overall progress: {progress_response.overallProgress * 100}%")
                progress_response = self.client.get_render_progress(
                    render_id=render_response.render_id,
                    bucket_name=render_response.bucket_name
                )

            if progress_response.done:
                return {
                    'status': 'done',
                    'message': 'Video processing complete',
                    'url': progress_response.outputFile
                }
            else:
                return {
                    'status': 'failed',
                    'message': 'Video processing failed'
                }

        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            logger.error(f"Stack trace: {e.__traceback__}")
            raise

    def cleanup(self):
        """Clean up temporary files"""
        pass 