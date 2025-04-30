import os
import json
import logging
import traceback
from typing import List, Dict, Any
import boto3
from .remotion_lambda_service import RemotionLambdaService

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RemotionService:
    def __init__(self):
        logger.info("Initializing RemotionService")
        self.lambda_service = RemotionLambdaService()
        
        # Initialize S3 client
        self.s3_client = boto3.client('s3')
        self.lambda_client = boto3.client('lambda')
        self.bucket_name = 'hyper-editor'  # Your S3 bucket name
        
        # Initialize Remotion settings
        self.serve_url = "https://remotionlambda-useast2-bvf5c7h3eb.s3.us-east-2.amazonaws.com/sites/caption-video/index.html"
        self.lambda_function_name = "remotion-render-4-0-293-mem2048mb-disk2048mb-120sec"
        
        logger.info("RemotionService initialized successfully")

    async def process_video(self, video_path: str, settings: dict) -> str:
        """Process a video using Remotion Lambda"""
        try:
            # Ensure the video URL is properly formatted
            if not video_path.startswith(('http://', 'https://')):
                # If it's a local file, upload it to S3 first
                s3_key = f"uploads/{os.path.basename(video_path)}"
                logger.info(f"Uploading local file to S3: {video_path} -> {s3_key}")
                self.s3_client.upload_file(video_path, self.bucket_name, s3_key)
                video_url = f"https://{self.bucket_name}.s3.us-east-2.amazonaws.com/{s3_key}"
                logger.info(f"File uploaded successfully. Video URL: {video_url}")
            else:
                video_url = video_path
                logger.info(f"Using provided video URL: {video_url}")

            # Prepare the render request
            render_request = {
                'type': 'render',
                'serveUrl': 'https://caption-video.remotion.lambda-url.us-east-2.on.aws',
                'composition': 'CaptionVideo',
                'outputLocation': {
                    's3': {
                        'bucketName': self.bucket_name,
                        'key': f"renders/{os.path.basename(video_path)}"
                    }
                },
                'codec': 'h264',
                'imageFormat': 'jpeg',
                'jpegQuality': 80,
                'inputProps': {
                    'videoSrc': video_url,
                    'font': settings.get('font', 'Montserrat-Bold'),
                    'color': settings.get('color', 'white'),
                    'fontSize': settings.get('fontSize', 32),
                    'position': settings.get('position', 0.7),
                    'maxWidth': settings.get('maxWidth', 1536),
                    'highlightColor': settings.get('highlightColor', '#FFD700')
                }
            }

            # Log the request details
            logger.info(f"Processing video: {video_url}")
            logger.info(f"Output location: s3://{self.bucket_name}/renders/{os.path.basename(video_path)}")
            logger.info(f"Full request payload: {json.dumps(render_request, indent=2)}")

            # Invoke the Lambda function
            response = self.lambda_client.invoke(
                FunctionName=self.lambda_function_name,
                Payload=json.dumps(render_request)
            )
            
            # Log response metadata
            logger.info("=== Lambda Response Metadata ===")
            logger.info(f"Status Code: {response['StatusCode']}")
            logger.info(f"Executed Version: {response.get('ExecutedVersion', 'N/A')}")
            logger.info(f"Function Error: {response.get('FunctionError', 'None')}")

            # Get and decode logs if available
            if 'LogResult' in response:
                import base64
                logs = base64.b64decode(response['LogResult']).decode('utf-8')
                logger.info("=== Lambda Execution Logs ===")
                logger.info(logs)

            # Check if we got a response
            payload = response['Payload'].read()
            logger.info("=== Lambda Response Payload ===")
            logger.info(f"Raw payload: {payload}")
            
            if not payload:
                raise Exception("Empty response from Remotion Lambda")

            # Parse the response
            try:
                response_payload = json.loads(payload)
                logger.info(f"Parsed response payload: {json.dumps(response_payload, indent=2)}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Lambda response: {str(e)}. Raw response: {payload}")
                raise Exception(f"Failed to parse Lambda response: {str(e)}. Response: {payload}")
            
            if 'errorMessage' in response_payload:
                logger.error(f"Lambda function returned error: {response_payload['errorMessage']}")
                raise Exception(f"Remotion Lambda error: {response_payload['errorMessage']}")

            if 'outputUrl' not in response_payload:
                logger.error(f"No outputUrl in response. Full response: {json.dumps(response_payload, indent=2)}")
                raise Exception(f"No outputUrl in response. Response: {response_payload}")

            logger.info(f"Successfully processed video. Output URL: {response_payload['outputUrl']}")
            return response_payload['outputUrl']

        except Exception as e:
            logger.error(f"Error processing video with Remotion: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise

    def cleanup(self):
        """Clean up temporary files"""
        self.lambda_service.cleanup() 