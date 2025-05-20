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
                    'captions': [
                        {
                            'text': 'hello how are you',
                            'startFrame': 0,
                            'endFrame': 90
                        }
                    ]
                },
                out_name=output_key
            )
            logger.info("starting render")
            # Start the render - this returns immediately
            render_response = self.client.render_media_on_lambda(render_params)
            logger.info(f"Render response: {render_response}")
            
            if not render_response:
                raise Exception("Failed to start render")

            # Store the bucket name for later use
            self.bucket_name = render_response.bucket_name

            # Return immediately with the render ID
            return {
                'status': 'processing',
                'renderId': render_response.render_id,
                'bucketName': render_response.bucket_name
            }

        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            logger.error(f"Stack trace: {e.__traceback__}")
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