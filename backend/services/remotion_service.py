import os
import logging
import json
import traceback
from remotion_lambda import RemotionClient, RenderMediaParams, Privacy, ValidStillImageFormats
from dotenv import load_dotenv
from typing import Dict, Any
from broll_analyzer import BrollAnalyzer
from utils.ffmpeg_utils import FFmpegUtils

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

    def process_video(self, video_url: str, output_key: str, captions: list = None, broll_enabled: bool = True) -> dict:
        try:
            logger.info(f"RemotionService processing video with broll_enabled={broll_enabled}")
            
            # Convert captions to Remotion format if provided
            remotion_captions = None
            if captions:
                logger.info(f"Converting {len(captions)} captions to Remotion format")
                remotion_captions = [
                    {
                        "text": caption["text"],
                        "startFrame": caption["startFrame"],
                        "endFrame": caption["endFrame"],
                        "words": caption.get("words", None)
                    }
                    for caption in captions
                ]
                #logger.info(f"Converted captions: {json.dumps(remotion_captions, indent=2)}")

            # Get b-roll clips if enabled
            broll_clips = []
            if broll_enabled:
                logger.info("B-roll enabled, starting b-roll processing")
                # Initialize BrollAnalyzer
                pexels_key = os.getenv('PEXELS_API_KEY')
                if not pexels_key:
                    raise ValueError("PEXELS_API_KEY is required for b-roll")
                
                broll_analyzer = BrollAnalyzer(pexels_key)
                logger.info("Initialized BrollAnalyzer")
                
                # Get video info
                main_width, main_height, video_duration = FFmpegUtils.get_video_info(video_url)
                logger.info(f"Video info: {main_width}x{main_height}, duration={video_duration}s")
                
                # Get b-roll suggestions
                broll_suggestions = broll_analyzer.get_broll_suggestions(
                    segments=captions,
                    video_duration=video_duration,
                    video_width=main_width,
                    video_height=main_height
                )
                logger.info(f"Got {len(broll_suggestions)} b-roll suggestions")
                
                # Process b-roll suggestions
                for suggestion in broll_suggestions:
                    if suggestion['broll_options']:
                        broll_option = suggestion['broll_options'][0]
                        # Allow for some difference in dimensions (50%)
                        width_diff = abs(broll_option.get('width', 0) - main_width) / main_width
                        height_diff = abs(broll_option.get('height', 0) - main_height) / main_height
                        
                        if width_diff > 0.5 or height_diff > 0.5:
                            logger.warning(f"B-roll clip dimensions ({broll_option.get('width')}x{broll_option.get('height')}) too different from main video ({main_width}x{main_height})")
                            continue
                            
                        broll_clip = {
                            'url': broll_option['url'],
                            'startFrame': int(suggestion['timestamp'] * 30),  # Convert seconds to frames at 30fps
                            'endFrame': int((suggestion['timestamp'] + suggestion['duration']) * 30),  # Convert seconds to frames at 30fps
                            'transitionDuration': 8  # 0.27 seconds at 30fps
                        }
                        logger.info(f"Added b-roll clip with timing: start={broll_clip['startFrame']} frames ({broll_clip['startFrame']/30:.2f}s), end={broll_clip['endFrame']} frames ({broll_clip['endFrame']/30:.2f}s)")
                        broll_clips.append(broll_clip)

            logger.info(f"Final b-roll clips count: {len(broll_clips)}")
            if broll_clips:
                logger.info(f"B-roll clips: {json.dumps(broll_clips, indent=2)}")

            # Set render request parameters
            input_props = {
                'videoSrc': video_url,
                'captions': remotion_captions or [],
                'font': 'Barlow-BlackItalic',
                'fontSize': 48,
                'color': 'white',
                'position': 'bottom',
                'highlightType': 'background',
                'brollClips': broll_clips
            }
            #logger.info(f"Input props for Remotion: {json.dumps(input_props, indent=2)}")

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