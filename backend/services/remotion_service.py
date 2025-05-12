import os
import json
import logging
import traceback
from typing import List, Dict, Any
import boto3
from backend.services.s3_service import S3Service

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RemotionService:
    def __init__(self):
        logger.info("Initializing RemotionService")
        # Initialize services
        self.s3_service = S3Service()
        
        # Initialize AWS clients
        self.s3_client = boto3.client('s3')
        self.lambda_client = boto3.client('lambda')
        self.bucket_name = 'hyper-editor'
        
        # Initialize Remotion settings
        self.serve_url = "https://remotionlambda-useast2-bvf5c7h3eb.s3.us-east-2.amazonaws.com/sites/caption-video/index.html"
        self.lambda_function_name = "remotion-render-4-0-272-mem2048mb-disk2048mb-120sec"
        self.region = "us-east-2"
        
        # Lambda configuration
        self.ram = 2048
        self.disk = 2048
        self.timeout = 120
        
        logger.info("RemotionService initialized successfully")

    async def process_video(self, video_url: str, settings: Dict[str, Any]) -> Dict[str, str]:
        """Process a video using Remotion Lambda"""
        try:
            # Extract the key from the video URL and ensure it has the uploads/ prefix
            key = video_url.split('/')[-1].split('?')[0]
            if not key.startswith('uploads/'):
                key = f"uploads/{key}"
            logger.info(f"Using S3 key: {key}")
            
            # Get the S3 URL for the video
            video_url = f"https://{self.bucket_name}.s3.us-east-2.amazonaws.com/{key}"
            
            # Verify the input video exists
            try:
                self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                logger.info(f"Input video exists in S3: {key}")
            except self.s3_client.exceptions.ClientError as e:
                logger.error(f"Input video not found in S3: {key}")
                raise Exception(f"Input video not found in S3: {key}")
            
            # Prepare the render request using the correct Remotion Lambda structure
            render_request = {
                'type': 'start',
                'serveUrl': self.serve_url,
                'composition': 'CaptionVideo',
                'inputProps': {
                    'videoSrc': video_url,
                    'captions': settings.get('captions', []),
                    'font': settings.get('font', "Barlow"),
                    'fontSize': settings.get('fontSize', 48),
                    'color': settings.get('color', "white"),
                    'position': settings.get('position', "bottom"),
                    'highlightType': settings.get('highlightType', "background"),
                    'useOffthreadVideo': True,
                    'onError': {
                        'fallbackVideo': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
                    }
                },
                'codec': 'h264',
                'imageFormat': 'jpeg',
                'maxRetries': 3,
                'privacy': 'public',
                'framesPerLambda': 100,
                'memorySizeInMb': self.ram,
                'diskSizeInMb': self.disk,
                'timeoutInSeconds': self.timeout,
                'outputLocation': {
                    's3': {
                        'bucketName': self.bucket_name,
                        'key': f"renders/{os.path.basename(key)}"
                    }
                }
            }

            # Log the request details
            logger.info(f"Processing video: {video_url}")
            logger.info(f"Output location: s3://{self.bucket_name}/renders/{os.path.basename(key)}")
            logger.info(f"Full request payload: {json.dumps(render_request, indent=2)}")
            logger.info(f"Lambda function: {self.lambda_function_name}")
            logger.info(f"Lambda configuration: RAM={self.ram}MB, Disk={self.disk}MB, Timeout={self.timeout}s")

            # Invoke Lambda for rendering (synchronously to get immediate feedback)
            response = self.lambda_client.invoke(
                FunctionName=self.lambda_function_name,
                Payload=json.dumps(render_request),
                InvocationType='RequestResponse'  # Changed to RequestResponse for immediate feedback
            )
            
            # Log response metadata and payload
            logger.info("=== Lambda Response Metadata ===")
            logger.info(f"Status Code: {response['StatusCode']}")
            logger.info(f"Executed Version: {response.get('ExecutedVersion', 'N/A')}")
            logger.info(f"Function Error: {response.get('FunctionError', 'None')}")
            
            # Get and decode the response payload
            if 'Payload' in response:
                payload = response['Payload'].read()
                try:
                    payload_json = json.loads(payload)
                    logger.info(f"Lambda Response Payload: {json.dumps(payload_json, indent=2)}")
                except json.JSONDecodeError:
                    logger.info(f"Raw Lambda Response Payload: {payload}")

            # Return immediately with renderId
            return {
                'status': 'processing',
                'message': 'Video processing started',
                'renderId': os.path.basename(key)  # Use the video filename as renderId
            }

        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise

    async def check_progress(self, render_id: str) -> Dict[str, Any]:
        """Check the progress of a video render"""
        try:
            # Check if the output file exists in S3
            try:
                self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=f"renders/{render_id}"
                )
                # If we get here, the file exists
                return {
                    'status': 'done',
                    'url': f"https://{self.bucket_name}.s3.us-east-2.amazonaws.com/renders/{render_id}"
                }
            except self.s3_client.exceptions.ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return {'status': 'processing'}
                else:
                    raise

        except Exception as e:
            logger.error(f"Error checking progress: {str(e)}")
            raise

    def cleanup(self):
        """Clean up temporary files"""
        pass 